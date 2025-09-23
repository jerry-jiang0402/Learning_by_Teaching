#!/usr/bin/env python3
"""
启动FastAPI后端服务器
"""
import uvicorn
import sys
import os

# 添加backend目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

if __name__ == "__main__":
    print("🚀 启动聊天机器人后端服务器...")
    print("📡 服务器地址: http://localhost:8000")
    print("📊 API文档: http://localhost:8000/docs")
    print("🔌 WebSocket端点: ws://localhost:8000/ws/chat")
    print("⏹️  按 Ctrl+C 停止服务器")
    print("-" * 50)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        app_dir="backend"
    )
