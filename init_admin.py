#!/usr/bin/env python3
"""
初始化管理员用户的脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from psy_admin_fastapi.database import get_db_session, engine
from psy_admin_fastapi.models import Base, AdminUser
from psy_admin_fastapi.security import get_password_hash
from psy_admin_fastapi.config import settings

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
        hashed_password = get_password_hash("admin")
        admin_user = AdminUser(
            username="admin",
            hashed_password=hashed_password
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print(f"管理员用户创建成功: admin/admin")
        
    except Exception as e:
        print(f"创建管理员用户失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()
