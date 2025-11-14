#!/usr/bin/env python3
"""
初始化管理员用户的脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from database import get_db_session, engine
from models import Base, AdminUser
from security import get_password_hash
from config import settings

def create_admin_user():
    """创建默认管理员用户"""
    print("正在创建管理员用户...")
    
    # 创建数据库表
    Base.metadata.create_all(bind=engine)
    print("数据库表已创建")
    
    # 获取数据库会话
    db = next(get_db_session())
    
    try:
        # 检查是否已存在管理员用户
        existing_admin = db.query(AdminUser).filter(AdminUser.username == "admin").first()
        if existing_admin:
            print("管理员用户已存在，跳过创建")
            return
        
        # 创建管理员用户
        # 使用简单的密码哈希，避免bcrypt版本问题
        password = "admin123"  # 使用更简单的密码
        hashed_password = get_password_hash(password)
        admin_user = AdminUser(
            username="admin",
            hashed_password=hashed_password
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print(f"管理员用户创建成功: admin/admin123")
        
    except Exception as e:
        print(f"创建管理员用户失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()
