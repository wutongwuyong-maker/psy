# models.py

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func # 用于获取当前时间
from datetime import datetime

from psy_admin_fastapi.database import Base # 从 .database 导入 Base

# 定义检测记录模型 (tests 表)
class Test(Base):
    __tablename__ = 'tests'
    id = Column(Integer, primary_key=True, index=True)
    student_fk_id = Column(Integer, ForeignKey('students.id'), nullable=False, comment='关联的学生ID')
    test_time = Column(DateTime(timezone=True), server_default=func.now(), comment='检测时间') # server_default 使用数据库服务器时间
    ai_summary = Column(Text, comment='AI评估总结')
    report_file_path = Column(String(255), comment='PDF报告文件路径')
    is_abnormal = Column(Boolean, default=False, comment='是否异常标记，方便筛选')
    status = Column(String(20), default='pending', comment='检测状态：pending, processing, completed, failed')

    # 定义与 Student 的多对一关系
    student = relationship("Student", back_populates="tests")
    # 定义与 Score 和 PhysiologicalData 的一对多关系
    scores = relationship("Score", back_populates="test")
    physiological_data = relationship("PhysiologicalData", back_populates="test")

# 定义问卷得分模型 (scores 表)
class Score(Base):
    __tablename__ = 'scores'
    id = Column(Integer, primary_key=True, index=True)
    test_fk_id = Column(Integer, ForeignKey('tests.id'), nullable=False, comment='关联的检测记录ID')
    module_name = Column(String(50), nullable=False, comment='问卷模块名，如学习焦虑、对人焦虑、孤独倾向、自责倾向')
    score = Column(Integer, nullable=False, comment='得分')
    max_score = Column(Integer, nullable=True, comment='满分')
    level = Column(String(20), nullable=True, comment='等级：重度、中度、轻度')
    questionnaire_feedback = Column(String(255), nullable=True, comment='问卷反馈或备注信息')

    # 定义与 Test 的多对一关系
    test = relationship("Test", back_populates="scores")

# 定义生理数据模型 (physiological_data 表)
class PhysiologicalData(Base):
    __tablename__ = 'physiological_data'
    id = Column(Integer, primary_key=True, index=True)
    test_fk_id = Column(Integer, ForeignKey('tests.id'), nullable=False, comment='关联的检测记录ID')
    data_key = Column(String(50), nullable=False, comment='数据项键，如心率、脑电alpha')
    data_value = Column(Float, nullable=False, comment='数据值')

    # 定义与 Test 的多对一关系
    test = relationship("Test", back_populates="physiological_data")

# 管理员用户表 (用于登录)
class AdminUser(Base):
    __tablename__ = 'admin_users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(80), unique=True, nullable=False)
    hashed_password = Column(String(128), nullable=False) # 存储哈希后的密码

# 登录日志表
class LoginLog(Base):
    __tablename__ = 'login_logs'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False, comment='登录用户名')
    login_time = Column(DateTime(timezone=True), server_default=func.now(), comment='登录时间')
    login_ip = Column(String(45), nullable=False)
    ip_address = Column(String(50), comment='登录IP地址')
    status = Column(String(20), nullable=False, default='success', comment='登录状态：success/fail')

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    student_id = Column(String(50), unique=True, nullable=False, index=True)
    class_name = Column(String(100), nullable=False)
    gender = Column(String(10), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    reports = relationship("Report", back_populates="student")
    tests = relationship("Test", back_populates="student")

class Report(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    student = relationship("Student", back_populates="reports")
