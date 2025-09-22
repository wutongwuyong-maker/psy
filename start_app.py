#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动脚本 - 解决模块导入问题
"""
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 启动FastAPI应用
if __name__ == "__main__":
    import uvicorn
    from psy_admin_fastapi.main import app
    
    print("正在启动心理检测管理系统...")
    print(f"项目根目录: {project_root}")
    print("服务器将在 http://localhost:8000 启动")
    print("按 Ctrl+C 停止服务器")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
