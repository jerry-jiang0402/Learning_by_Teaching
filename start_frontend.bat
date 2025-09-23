@echo off
echo 🚀 启动Vue前端开发服务器...
echo 🌐 前端地址: http://localhost:5173
echo ⏹️  按 Ctrl+C 停止服务器
echo --------------------------------------------------

cd frontend

REM 检查是否已安装依赖
if not exist "node_modules" (
    echo 📦 正在安装依赖...
    npm install
)

REM 启动开发服务器
npm run dev
