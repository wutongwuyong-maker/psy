#!/usr/bin/env python3
"""
测试后端启动的脚本
"""
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """测试所有必要的导入"""
    try:
        print("测试基本模块导入...")
        import pandas as pd
        print("✓ pandas 导入成功")
        
        print("测试数据库模块导入...")
        import database
        print("✓ database 导入成功")
        
        print("测试模型模块导入...")
        import models
        print("✓ models 导入成功")
        
        print("测试CRUD模块导入...")
        import crud
        print("✓ crud 导入成功")
        
        print("测试schemas模块导入...")
        import schemas
        print("✓ schemas 导入成功")
        
        print("测试安全模块导入...")
        import security
        print("✓ security 导入成功")
        
        print("测试工具模块导入...")
        from utils import cache, concurrent, logging_utils
        print("✓ utils 模块导入成功")
        
        print("测试配置模块导入...")
        import config
        print("✓ config 导入成功")
        
        print("所有模块导入测试通过！")
        return True
        
    except Exception as e:
        print(f"✗ 导入失败: {e}")
        return False

def test_main():
    """测试主模块导入"""
    try:
        print("测试主模块导入...")
        import main
        print("✓ main 导入成功")
        return True
    except Exception as e:
        print(f"✗ 主模块导入失败: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("心理检测管理系统 - 启动测试")
    print("=" * 50)
    
    # 测试所有导入
    imports_ok = test_imports()
    
    if imports_ok:
        # 测试主模块
        main_ok = test_main()
        
        if main_ok:
            print("\n🎉 所有测试通过！系统可以正常启动。")
            print("\n启动命令:")
            print("cd d:/shiyanshi_laoshi/psy_admin_fastapi")
            print("python main.py")
        else:
            print("\n❌ 主模块导入失败，请检查相关配置。")
    else:
        print("\n❌ 模块导入失败，请检查依赖包安装。")
    
    print("=" * 50)
