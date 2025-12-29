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
from teaching_flow import TeachingFlowManager
from knowledge_points import ALGORITHM_INFO
# from langchain_openai import ChatOpenAI
# from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

# 加载环境变量，强制覆盖系统环境变量
load_dotenv(override=True)

# Pydantic模型（v2兼容）
class MessageModel(BaseModel):
    content: str
    
class AlgorithmSelection(BaseModel):
    algorithm: str
    
class ChatMessage(BaseModel):
    id: int
    type: str
    content: str
    timestamp: str
    sender: str

app = FastAPI(title="AI Learning Platform API", version="1.0.0")

# 初始化OpenAI客户端
openai_client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
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
        self.teaching_flow = TeachingFlowManager()  # 新增教学流程管理器

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        
        # 每次新连接都重置会话状态，开始全新的学习对话
        self.reset_session()
        
        # 发送算法选择提示
        selection_message = {
            "id": 1,
            "type": "system",
            "content": "algorithm_selection",
            "timestamp": datetime.now().isoformat(),
            "sender": "System",
            "algorithms": ALGORITHM_INFO
        }
        await self.broadcast(selection_message)
    
    def reset_session(self):
        """重置学习会话，清除所有历史记录和状态"""
        self.chat_history.clear()
        self.conversation_complete = False
        self.teaching_flow = TeachingFlowManager()  # 创建新的教学流程管理器

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
            # 使用新的教学流程管理器生成回复（异步调用）
            ai_reply = await self.teaching_flow.get_next_ai_response(user_message_content)
            
            # 检查是否完成所有知识点
            status = self.teaching_flow.get_current_status()
            if status["phase"] == "all_completed":
                self.conversation_complete = True
            
            # 🔋 获取能量统计数据
            energy_stats = self.teaching_flow.energy_manager.get_stats()
            
            ai_response = {
                "id": len(self.chat_history) + 1,
                "type": "bot",
                "content": ai_reply,
                "timestamp": datetime.now().isoformat(),
                "sender": "Algorithm Buddy",
                "teaching_phase": status["phase"],
                "current_knowledge_point": status["current_knowledge_point"]["title"] if status["current_knowledge_point"] else None,
                "energy_stats": energy_stats  # 🔋 包含能量数据
            }
            
            await self.broadcast(ai_response)
            
        except Exception as e:
            # If error occurs, send error message
            error_response = {
                "id": len(self.chat_history) + 1,
                "type": "bot",
                "content": f"Sorry, I encountered some issues responding. Please try again later. Error: {str(e)}",
                "timestamp": datetime.now().isoformat(),
                "sender": "Algorithm Buddy"
            }
            
            await self.broadcast(error_response)

manager = ConnectionManager()

# 旧的评估和GPT-4功能已移除，现在使用教学流程管理器

@app.get("/")
async def root():
    return {"message": "AI Learning Platform API Server Running"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/algorithms")
async def get_algorithms():
    return {"algorithms": ALGORITHM_INFO}

@app.get("/api/energy")
async def get_energy_stats():
    """🔋 获取当前能量统计数据"""
    energy_stats = manager.teaching_flow.energy_manager.get_stats()
    return {"energy": energy_stats}

@app.post("/api/select-algorithm")
async def select_algorithm(selection: AlgorithmSelection):
    success = manager.teaching_flow.select_algorithm(selection.algorithm)
    if success:
        # 开始学习会话
        opening_content = await manager.teaching_flow.start_session()
        initial_message = {
            "id": len(manager.chat_history) + 1,
            "type": "bot",
            "content": opening_content,
            "timestamp": datetime.now().isoformat(),
            "sender": "Algorithm Buddy"
        }
        await manager.broadcast(initial_message)
        return {"success": True, "message": "Algorithm selected successfully"}
    else:
        return {"success": False, "message": "Invalid algorithm selection"}

# ✅ 主动查看二级小点的端点
class ViewSubItemRequest(BaseModel):
    topic_id: str
    sub_item_id: str

@app.post("/api/view_sub_item")
async def view_sub_item(request: ViewSubItemRequest):
    """学生主动查看二级小点"""
    result = manager.teaching_flow.manually_view_sub_item(
        request.topic_id,
        request.sub_item_id
    )
    return result

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            user_content = message_data.get("content", "")
            score_multiplier = message_data.get("score_multiplier", 1.0)  # 🕐 获取分数倍数
            
            # Teaching Helper: Check teaching quality and relevance
            helper_evaluation = None
            energy_gain = None
            energy_reason = None
            
            if manager.teaching_flow.knowledge_manager:
                helper_evaluation = await manager.teaching_flow.check_teaching_quality(user_content, score_multiplier)
                
                # 🔋 提取能量数据
                energy_gain = helper_evaluation.get("energy_gain", 0)
                energy_reason = helper_evaluation.get("energy_reason", "")
                
                # If not relevant, send warning and reject message
                if not helper_evaluation.get("is_relevant", True):
                    warning_message = {
                        "id": len(manager.chat_history) + 1,
                        "type": "warning",
                        "content": helper_evaluation.get("warning_message", "Please keep the discussion relevant to the current knowledge point"),
                        "timestamp": datetime.now().isoformat(),
                        "sender": "Teaching Helper"
                    }
                    await manager.broadcast(warning_message)
                    continue  # Skip this message, don't add to history
                
                # ✅ 检测并解锁二级小点
                unlocked_sub_items = await manager.teaching_flow.check_and_unlock_sub_items(user_content, score_multiplier)
                if unlocked_sub_items:
                    # 累加所有能量奖励
                    for item in unlocked_sub_items:
                        item_energy = item.get("energy_gain", 0)
                        if item_energy > 0:
                            energy_gain += item_energy
                            # 合并事件描述
                            if "events" in item:
                                energy_reason += " " + " ".join(item["events"])
            
            # Handle user message
            current_time = datetime.now()
            user_message = {
                "id": len(manager.chat_history) + 1,
                "type": "user",
                "content": user_content,
                "timestamp": current_time.isoformat(),
                "sender": "You",
                "energy_gain": energy_gain,  # 🔋 能量增益
                "energy_reason": energy_reason  # 🔋 能量原因
            }
            
            await manager.broadcast(user_message)
            
            # 生成AI回复
            await manager.generate_ai_response(user_content)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/api/chat/history")
async def get_chat_history():
    return {"messages": manager.chat_history}

@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    # Get teaching flow statistics
    if manager.teaching_flow.knowledge_manager:
        teaching_stats = manager.teaching_flow.get_dashboard_stats()
        return {
            "total_messages": len(manager.chat_history),
            "total_knowledge_points": teaching_stats["total_knowledge_points"],
            "completed_knowledge_points": teaching_stats["completed_knowledge_points"],
            "current_knowledge_point": teaching_stats["current_knowledge_point"],
            "progress_percentage": teaching_stats["progress_percentage"],
            "current_phase": teaching_stats["current_phase"],
            "knowledge_points_detail": teaching_stats["knowledge_points_detail"],
            "selected_algorithm": manager.teaching_flow.algorithm_selected,
            "teaching_evaluations": teaching_stats["teaching_evaluations"],
            "energy_stats": teaching_stats["energy_stats"],  # 🔋 包含能量数据
            "topics": teaching_stats.get("topics", []),  # ✅ 两级 Topic 结构
            "current_topic_index": teaching_stats.get("current_topic_index", 0)  # ✅ 当前 Topic 索引
        }
    else:
        return {
            "total_messages": len(manager.chat_history),
            "total_knowledge_points": 0,
            "completed_knowledge_points": 0,
            "current_knowledge_point": "Please select an algorithm",
            "progress_percentage": 0,
            "current_phase": "algorithm_selection",
            "knowledge_points_detail": [],
            "selected_algorithm": None,
            "teaching_evaluations": []
        }

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    if debug:
        # 开发模式：使用导入字符串以支持热重载
        uvicorn.run("main:app", host=host, port=port, reload=True)
    else:
        # 生产模式：直接使用app对象
        uvicorn.run(app, host=host, port=port, reload=False)
