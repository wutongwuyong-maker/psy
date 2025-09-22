#!/bin/bash

# 学校心理监测系统部署脚本
# 用于自动化部署后端和前端

set -e

echo "开始部署学校心理监测系统..."

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python3"
    exit 1
fi

# 检查Node.js环境
if ! command -v node &> /dev/null; then
    echo "错误: 未找到Node.js，请先安装Node.js"
    exit 1
fi

# 后端部署
echo "开始部署后端..."
cd psy_admin_fastapi

# 安装Python依赖
echo "安装Python依赖..."
pip3 install -r requirements.txt

# 检查环境变量文件
if [ ! -f ".env" ]; then
    echo "警告: 未找到.env文件，请复制env.example并配置"
    if [ -f "env.example" ]; then
        cp env.example .env
        echo "已复制env.example到.env，请编辑.env文件配置数据库等信息"
    fi
fi

# 运行数据库迁移
echo "运行数据库迁移..."
python3 migrate.py upgrade

# 启动后端服务（后台运行）
echo "启动后端服务..."
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > app.log 2>&1 &
echo $! > backend.pid
echo "后端服务已启动，PID: $(cat backend.pid)"

cd ..

# 前端部署
echo "开始部署前端..."
cd psy_admin_vue

# 安装Node.js依赖
echo "安装Node.js依赖..."
npm install

# 检查环境变量文件
if [ ! -f ".env.development" ]; then
    echo "警告: 未找到.env.development文件"
    if [ -f "env.development" ]; then
        cp env.development .env.development
        echo "已复制env.development到.env.development"
    fi
fi

if [ ! -f ".env.production" ]; then
    echo "警告: 未找到.env.production文件"
    if [ -f "env.production" ]; then
        cp env.production .env.production
        echo "已复制env.production到.env.production"
    fi
fi

# 构建前端
echo "构建前端..."
npm run build

# 启动前端服务（如果使用开发模式）
if [ "$1" = "dev" ]; then
    echo "启动前端开发服务器..."
    npm run serve
else
    echo "前端构建完成，请配置Web服务器（如Nginx）来提供静态文件服务"
fi

cd ..

echo "部署完成！"
echo "后端服务: http://localhost:8000"
echo "前端服务: http://localhost:8080 (开发模式)"
echo ""
echo "管理命令:"
echo "  停止后端: kill \$(cat psy_admin_fastapi/backend.pid)"
echo "  查看后端日志: tail -f psy_admin_fastapi/app.log"
echo "  数据库迁移: cd psy_admin_fastapi && python3 migrate.py upgrade"

