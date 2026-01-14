#!/usr/bin/env python3
"""
Start FastAPI Backend Server
"""
import uvicorn
import sys
import os

# Add backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

if __name__ == "__main__":
    print("Starting Learning by Teaching Backend Server...")
    print("Server URL: http://localhost:8000")
    print("API Docs: http://localhost:8000/docs")
    print("WebSocket: ws://localhost:8000/ws/chat")
    print("Press Ctrl+C to stop")
    print("-" * 50)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        app_dir="backend"
    )
