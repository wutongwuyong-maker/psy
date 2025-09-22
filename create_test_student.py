#!/usr/bin/env python3
"""
创建测试学生数据的脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from database import get_db_session
from models import Student
from datetime import datetime

def create_test_students():
    """创建测试学生数据"""
    print("正在创建测试学生数据...")
    
    # 获取数据库会话
    db = next(get_db_session())
    
    try:
        # 检查是否已存在学生数据
        existing_students = db.query(Student).count()
        if existing_students > 0:
            print(f"数据库中已有 {existing_students} 条学生记录，跳过创建")
            return
        
        # 创建测试学生数据
        test_students = [
            Student(
                name="张三",
                student_id="S001",
                class_name="一年级一班",
                gender="男",
                created_at=datetime.utcnow()
            ),
            Student(
                name="李四",
                student_id="S002",
                class_name="一年级二班",
                gender="女",
                created_at=datetime.utcnow()
            ),
            Student(
                name="王五",
                student_id="S003",
                class_name="二年级一班",
                gender="男",
                created_at=datetime.utcnow()
            )
        ]
        
        for student in test_students:
            db.add(student)
        
        db.commit()
        print(f"成功创建 {len(test_students)} 条测试学生记录")
        
    except Exception as e:
        print(f"创建测试学生数据失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_students()
