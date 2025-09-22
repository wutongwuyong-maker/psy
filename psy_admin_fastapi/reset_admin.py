#!/usr/bin/env python3
"""
重置管理员用户密码的脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from database import get_db_session
from models import AdminUser
from security import get_password_hash

def reset_admin_password():
    """重置管理员用户密码"""
    print("正在重置管理员用户密码...")
    
    # 获取数据库会话
    db = next(get_db_session())
    
    try:
        # 获取管理员用户
        admin_user = db.query(AdminUser).filter(AdminUser.username == "admin").first()
        if not admin_user:
            print("管理员用户不存在")
            return
        
        # 生成新的密码哈希
        new_password = "admin123"
        new_hash = get_password_hash(new_password)
        
        # 更新密码
        admin_user.hashed_password = new_hash
        db.commit()
        
        print(f"管理员用户密码已重置: {admin_user.username}/{new_password}")
        
    except Exception as e:
        print(f"重置管理员密码失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reset_admin_password()
