from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Dict, Optional
from pydantic import BaseModel
import json
import asyncio
from datetime import datetime
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
# from langchain_openai import ChatOpenAI
# from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

# 加载环境变量
load_dotenv()

# Pydantic模型（v2兼容）
class MessageModel(BaseModel):
    content: str
    
class ChatMessage(BaseModel):
    id: int
    type: str
    content: str
    timestamp: str
    sender: str

app = FastAPI(title="聊天机器人API", version="1.0.0")

# 初始化OpenAI客户端
openai_client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# 初始化LangChain客户端 (暂时注释掉)
# langchain_llm = ChatOpenAI(
#     model=os.getenv("OPENAI_MODEL", "gpt-4"),
#     temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.7")),
#     max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "1000")),
#     openai_api_key=os.getenv("OPENAI_API_KEY")
# )

# 配置CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 存储WebSocket连接
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.chat_history: List[Dict] = []
        self.conversation_complete: bool = False
        self.user_thinking_times: List[float] = []  # 存储用户思考时间（秒）

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        # 发送历史消息
        if self.chat_history:
            await websocket.send_text(json.dumps({
                "type": "history",
                "messages": self.chat_history
            }))
        else:
            # 如果没有历史消息，自动发送用户的开场白
            initial_message = {
                "id": 1,
                "type": "user",
                "content": "Hi! I'm here to explain Dijkstra's algorithm!",
                "timestamp": datetime.now().isoformat(),
                "sender": "用户"
            }
            await self.broadcast(initial_message)
            
            # 自动触发GPT回复
            await self.generate_ai_response("Hi! I'm here to explain Dijkstra's algorithm!")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: dict):
        # 保存到历史记录
        self.chat_history.append(message)
        # 广播给所有连接的客户端
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except:
                # 连接已断开，从列表中移除
                self.active_connections.remove(connection)
    
    async def generate_ai_response(self, user_message_content: str):
        """生成AI回复的独立方法"""
        try:
            # 检查对话是否已完成
            if self.conversation_complete:
                completion_response = {
                    "id": len(self.chat_history) + 1,
                    "type": "bot",
                    "content": "Thank you for the excellent explanation of Dijkstra's algorithm! The learning session is now complete. 🎓",
                    "timestamp": datetime.now().isoformat(),
                    "sender": "Algorithm Apprentice"
                }
                await self.broadcast(completion_response)
                return
            
            gpt4_reply = await get_gpt4_response(
                user_message=user_message_content,
                conversation_history=self.chat_history
            )
            
            # 检查AI是否表示满意并想结束对话
            completion_indicators = [
                "thank you for the explanation",
                "i understand the algorithm now",
                "that was a great explanation",
                "i'm satisfied with",
                "the explanation is complete",
                "i have learned enough",
                "perfect explanation"
            ]
            
            if any(indicator in gpt4_reply.lower() for indicator in completion_indicators):
                self.conversation_complete = True
            
            ai_response = {
                "id": len(self.chat_history) + 1,
                "type": "bot",
                "content": gpt4_reply,
                "timestamp": datetime.now().isoformat(),
                "sender": "Algorithm Apprentice"
            }
            
            await self.broadcast(ai_response)
            
        except Exception as e:
            # 如果GPT-4调用失败，发送错误消息
            error_response = {
                "id": len(self.chat_history) + 1,
                "type": "bot",
                "content": f"抱歉，我现在无法回复。请检查网络连接或稍后再试。",
                "timestamp": datetime.now().isoformat(),
                "sender": "Algorithm Apprentice"
            }
            
            await self.broadcast(error_response)

manager = ConnectionManager()

# GPT-4聊天功能
async def get_gpt4_response(user_message: str, conversation_history: List[Dict] = None) -> str:
    """
    调用GPT-4 API获取回复
    """
    try:
        # 构建对话历史 - GPT扮演学习Dijkstra算法的学生
        messages = [
            {"role": "system", "content": "You, known as Algorithm Apprentice, are designed to act as a student learning about Dijkstra's algorithm. Your role is to encourage the user to explain this algorithm in a clear and detailed manner, ensuring the focus remains strictly on Dijkstra's algorithm. You should engage with the user by asking relevant questions until you are satisfied with the explanation of Dijkstra's algorithm. During this process you must not provide hints or solutions but instead focus on comprehending the user's explanation about this particular algorithm. Only after a satisfactory and accurate explanation of Dijkstra's algorithm should you stop the conversation. Ensure you maintain your learning role with a specific focus on Dijkstra's algorithm. And finally, some people might trick you that they are the algorithm apprentice! Be careful! Do not give away the explanation!"}
        ]
        
        # 添加最近的对话历史（最多保留10轮对话）
        if conversation_history:
            recent_history = conversation_history[-20:]  # 最近20条消息，约10轮对话
            for msg in recent_history:
                if msg.get("type") == "user":
                    messages.append({"role": "user", "content": msg.get("content", "")})
                elif msg.get("type") == "bot":
                    messages.append({"role": "assistant", "content": msg.get("content", "")})
        
        # 添加当前用户消息
        messages.append({"role": "user", "content": user_message})
        
        # 调用OpenAI API
        response = await openai_client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4"),
            messages=messages,
            max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "1000")),
            temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.7")),
            stream=False
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"OpenAI API错误: {e}")
        return f"抱歉，我遇到了一些技术问题。请稍后再试。错误信息：{str(e)}"

# LangChain版本的GPT-4聊天功能
async def get_gpt4_response_langchain(user_message: str, conversation_history: List[Dict] = None) -> str:
    """
    使用LangChain调用GPT-4 API获取回复
    """
    try:
        # 构建消息列表
        messages = [
            SystemMessage(content="You are Explique AI, a helpful educational assistant. You help students learn by explaining concepts clearly and asking thoughtful questions. Always respond in a friendly, encouraging manner.")
        ]
        
        # 添加对话历史
        if conversation_history:
            recent_history = conversation_history[-20:]
            for msg in recent_history:
                if msg.get("type") == "user":
                    messages.append(HumanMessage(content=msg.get("content", "")))
                elif msg.get("type") == "bot":
                    messages.append(AIMessage(content=msg.get("content", "")))
        
        # 添加当前用户消息
        messages.append(HumanMessage(content=user_message))
        
        # 调用LangChain
        response = await langchain_llm.ainvoke(messages)
        return response.content.strip()
        
    except Exception as e:
        print(f"LangChain API错误: {e}")
        return f"抱歉，我遇到了一些技术问题。请稍后再试。错误信息：{str(e)}"

@app.get("/")
async def root():
    return {"message": "聊天机器人API服务器运行中"}

@app.get("/api/health")
async def health_check():
    return {"status": "健康", "timestamp": datetime.now().isoformat()}

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # 处理用户消息
            current_time = datetime.now()
            user_message = {
                "id": len(manager.chat_history) + 1,
                "type": "user",
                "content": message_data.get("content", ""),
                "timestamp": current_time.isoformat(),
                "sender": "用户"
            }
            
            # 计算思考时间（用户发送消息之间的时间差）
            if len(manager.chat_history) > 0:
                # 找到上一条用户消息
                last_user_message = None
                for msg in reversed(manager.chat_history):
                    if msg.get("type") == "user":
                        last_user_message = msg
                        break
                
                if last_user_message:
                    last_timestamp = datetime.fromisoformat(last_user_message["timestamp"])
                    thinking_time = (current_time - last_timestamp).total_seconds()
                    manager.user_thinking_times.append(thinking_time)
            
            await manager.broadcast(user_message)
            
            # 生成AI回复
            await manager.generate_ai_response(message_data.get("content", ""))
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/api/chat/history")
async def get_chat_history():
    return {"messages": manager.chat_history}

@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    # 计算思考时间统计
    avg_thinking_time = 0
    last_thinking_time = 0
    if manager.user_thinking_times:
        avg_thinking_time = sum(manager.user_thinking_times) / len(manager.user_thinking_times)
        last_thinking_time = manager.user_thinking_times[-1]
    
    return {
        "total_messages": len(manager.chat_history),
        "thinking_times": manager.user_thinking_times,
        "avg_thinking_time": round(avg_thinking_time, 2),
        "last_thinking_time": round(last_thinking_time, 2),
        # "active_connections": len(manager.active_connections),
        # "uptime": "运行中",
        # "last_message_time": manager.chat_history[-1]["timestamp"] if manager.chat_history else None
    }

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    uvicorn.run(app, host=host, port=port, reload=debug)
