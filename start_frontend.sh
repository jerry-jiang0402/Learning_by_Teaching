#!/bin/bash
echo "🚀 启动Vue前端开发服务器..."
echo "🌐 前端地址: http://localhost:5173"
echo "⏹️  按 Ctrl+C 停止服务器"
echo "--------------------------------------------------"

cd frontend

# 检查是否已安装依赖
if [ ! -d "node_modules" ]; then
    echo "📦 正在安装依赖..."
    npm install
fi

# 启动开发服务器
npm run dev
