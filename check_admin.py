#!/usr/bin/env python3
"""
检查管理员用户密码的脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from database import get_db_session
from models import AdminUser
from security import verify_password, get_password_hash

def check_admin_password():
    """检查管理员用户密码"""
    print("正在检查管理员用户密码...")
    
    # 获取数据库会话
    db = next(get_db_session())
    
    try:
        # 获取管理员用户
        admin_user = db.query(AdminUser).filter(AdminUser.username == "admin").first()
        if not admin_user:
            print("管理员用户不存在")
            return
        
        print(f"管理员用户: {admin_user.username}")
        print(f"哈希密码: {admin_user.hashed_password}")
        
        # 测试密码
        test_password = "admin"
        is_valid = verify_password(test_password, admin_user.hashed_password)
        print(f"密码 '{test_password}' 验证结果: {is_valid}")
        
        # 生成新的哈希密码
        new_hash = get_password_hash(test_password)
        print(f"新哈希密码: {new_hash}")
        
    except Exception as e:
        print(f"检查管理员密码失败: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_admin_password()
