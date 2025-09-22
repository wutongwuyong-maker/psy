#!/usr/bin/env python3
"""
完整的API测试套件
"""
import pytest
import sys
import os
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from psy_admin_fastapi.main import app
from psy_admin_fastapi.database import get_db
from psy_admin_fastapi.models import Base, Student, Test, Score, PhysiologicalData, AdminUser
from psy_admin_fastapi.crud import create_student, create_test_data, create_client_test_data
from psy_admin_fastapi.schemas import StudentCreate, TestDataUpload
from psy_admin_fastapi.security import get_password_hash

# 测试数据库URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db):
    return TestClient(app)

@pytest.fixture
def test_student(db):
    """创建测试学生"""
    student_data = StudentCreate(
        name="张三",
        student_id="T001",
        class_name="计算机1班",
        gender="男"
    )
    return create_student(db, student_data)

@pytest.fixture
def test_admin_user(db):
    """创建测试管理员用户"""
    admin_user = AdminUser(
        username="admin",
        hashed_password=get_password_hash("password123")
    )
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    return admin_user

class TestStudentAPI:
    """学生管理API测试"""
    
    def test_create_student(self, client, db):
        """测试创建学生"""
        student_data = {
            "name": "李四",
            "student_id": "T002",
            "class_name": "计算机2班",
            "gender": "女"
        }
        response = client.post("/api/students/", json=student_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "李四"
        assert data["student_id"] == "T002"
    
    def test_create_duplicate_student(self, client, db, test_student):
        """测试创建重复学号的学生"""
        student_data = {
            "name": "王五",
            "student_id": "T001",  # 重复学号
            "class_name": "计算机3班",
            "gender": "男"
        }
        response = client.post("/api/students/", json=student_data)
        assert response.status_code == 400
    
    def test_get_student(self, client, db, test_student):
        """测试获取学生信息"""
        response = client.get(f"/api/students/{test_student.student_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "张三"
        assert data["student_id"] == "T001"
    
    def test_get_nonexistent_student(self, client, db):
        """测试获取不存在的学生"""
        response = client.get("/api/students/XXXXX")
        assert response.status_code == 404
    
    def test_update_student(self, client, db, test_student):
        """测试更新学生信息"""
        update_data = {
            "name": "张三（更新）",
            "class_name": "计算机1班（更新）"
        }
        response = client.put(f"/api/students/{test_student.student_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "张三（更新）"
        assert data["class_name"] == "计算机1班（更新）"
    
    def test_delete_student(self, client, db, test_student):
        """测试删除学生"""
        response = client.delete(f"/api/students/{test_student.student_id}")
        assert response.status_code == 200
        
        # 验证学生已被删除
        response = client.get(f"/api/students/{test_student.student_id}")
        assert response.status_code == 404
    
    def test_get_students_with_filters(self, client, db):
        """测试带筛选条件的学生列表"""
        # 创建多个学生
        students = [
            {"name": "学生1", "student_id": "S001", "class_name": "计算机1班", "gender": "男"},
            {"name": "学生2", "student_id": "S002", "class_name": "计算机1班", "gender": "女"},
            {"name": "学生3", "student_id": "S003", "class_name": "计算机2班", "gender": "男"},
        ]
        
        for student_data in students:
            client.post("/api/students/", json=student_data)
        
        # 测试按班级筛选
        response = client.get("/api/students/?class_name=计算机1班")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        
        # 测试按性别筛选
        response = client.get("/api/students/?gender=男")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

class TestTestRecordAPI:
    """检测记录API测试"""
    
    def test_create_test_data(self, client, db, test_student):
        """测试创建检测数据"""
        test_data = {
            "user_id": "T001",
            "name": "张三",
            "gender": "男",
            "age": 20,
            "test_time": datetime.now().isoformat(),
            "questionnaire_scores": {
                "焦虑": 12,
                "抑郁": 8,
                "压力": 15
            },
            "physiological_data_summary": {
                "心率": 85.0,
                "脑电alpha": 13.2
            },
            "ai_summary": "检测结果正常",
            "report_file_path": "reports/test.pdf"
        }
        response = client.post("/api/test-records/", json=test_data)
        assert response.status_code == 200
        data = response.json()
        assert data["student_fk_id"] == test_student.id
        assert data["is_abnormal"] == False
    
    def test_create_abnormal_test_data(self, client, db, test_student):
        """测试创建异常检测数据"""
        test_data = {
            "user_id": "T001",
            "name": "张三",
            "gender": "男",
            "age": 20,
            "test_time": datetime.now().isoformat(),
            "questionnaire_scores": {
                "焦虑": 18,  # 超过阈值
                "抑郁": 8,
                "压力": 12
            },
            "physiological_data_summary": {
                "心率": 85.0,
                "脑电alpha": 13.2
            },
            "ai_summary": "检测结果异常",
            "report_file_path": "reports/test.pdf"
        }
        response = client.post("/api/test-records/", json=test_data)
        assert response.status_code == 200
        data = response.json()
        assert data["is_abnormal"] == True
    
    def test_get_test_records(self, client, db, test_student):
        """测试获取检测记录列表"""
        # 创建测试数据
        test_data = {
            "user_id": "T001",
            "name": "张三",
            "gender": "男",
            "age": 20,
            "test_time": datetime.now().isoformat(),
            "questionnaire_scores": {
                "焦虑": 12,
                "抑郁": 8,
                "压力": 15
            },
            "physiological_data_summary": {
                "心率": 85.0,
                "脑电alpha": 13.2
            },
            "ai_summary": "检测结果正常",
            "report_file_path": "reports/test.pdf"
        }
        client.post("/api/test-records/", json=test_data)
        
        response = client.get("/api/test-records/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
    
    def test_get_test_record_detail(self, client, db, test_student):
        """测试获取检测记录详情"""
        # 创建测试数据
        test_data = {
            "user_id": "T001",
            "name": "张三",
            "gender": "男",
            "age": 20,
            "test_time": datetime.now().isoformat(),
            "questionnaire_scores": {
                "焦虑": 12,
                "抑郁": 8,
                "压力": 15
            },
            "physiological_data_summary": {
                "心率": 85.0,
                "脑电alpha": 13.2
            },
            "ai_summary": "检测结果正常",
            "report_file_path": "reports/test.pdf"
        }
        create_response = client.post("/api/test-records/", json=test_data)
        record_id = create_response.json()["id"]
        
        response = client.get(f"/api/test-records/{record_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == record_id
        assert data["student"]["name"] == "张三"
    
    def test_get_test_records_with_filters(self, client, db, test_student):
        """测试带筛选条件的检测记录"""
        # 创建正常数据
        normal_data = {
            "user_id": "T001",
            "name": "张三",
            "gender": "男",
            "age": 20,
            "test_time": datetime.now().isoformat(),
            "questionnaire_scores": {
                "焦虑": 12,
                "抑郁": 8,
                "压力": 15
            },
            "physiological_data_summary": {
                "心率": 85.0,
                "脑电alpha": 13.2
            },
            "ai_summary": "检测结果正常",
            "report_file_path": "reports/test.pdf"
        }
        client.post("/api/test-records/", json=normal_data)
        
        # 创建异常数据
        abnormal_data = {
            "user_id": "T001",
            "name": "张三",
            "gender": "男",
            "age": 20,
            "test_time": datetime.now().isoformat(),
            "questionnaire_scores": {
                "焦虑": 18,  # 异常
                "抑郁": 8,
                "压力": 12
            },
            "physiological_data_summary": {
                "心率": 85.0,
                "脑电alpha": 13.2
            },
            "ai_summary": "检测结果异常",
            "report_file_path": "reports/test.pdf"
        }
        client.post("/api/test-records/", json=abnormal_data)
        
        # 测试按异常状态筛选
        response = client.get("/api/test-records/?is_abnormal=true")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["is_abnormal"] == True

class TestAuthenticationAPI:
    """认证API测试"""
    
    def test_login_success(self, client, db, test_admin_user):
        """测试登录成功"""
        login_data = {
            "username": "admin",
            "password": "password123"
        }
        response = client.post("/api/auth/login", data=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_failure(self, client, db):
        """测试登录失败"""
        login_data = {
            "username": "wrong_user",
            "password": "wrong_password"
        }
        response = client.post("/api/auth/login", data=login_data)
        assert response.status_code == 401
    
    def test_protected_endpoint_without_token(self, client, db):
        """测试无token访问受保护接口"""
        response = client.get("/api/students/")
        assert response.status_code == 401
    
    def test_protected_endpoint_with_token(self, client, db, test_admin_user):
        """测试有token访问受保护接口"""
        # 先登录获取token
        login_data = {
            "username": "admin",
            "password": "password123"
        }
        login_response = client.post("/api/auth/login", data=login_data)
        token = login_response.json()["access_token"]
        
        # 使用token访问受保护接口
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/students/", headers=headers)
        assert response.status_code == 200

class TestClientAPI:
    """客户端对接API测试"""
    
    def test_validate_student_success(self, client, db, test_student):
        """测试学号验证成功"""
        request_data = {
            "student_id": "T001"
        }
        response = client.post("/api/client/validate-student", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["exists"] == True
        assert data["student_info"]["name"] == "张三"
    
    def test_validate_student_failure(self, client, db):
        """测试学号验证失败"""
        request_data = {
            "student_id": "NONEXISTENT"
        }
        response = client.post("/api/client/validate-student", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["exists"] == False
    
    def test_get_student_test_status(self, client, db, test_student):
        """测试获取学生检测状态"""
        # 创建检测记录
        test_data = {
            "user_id": "T001",
            "name": "张三",
            "gender": "男",
            "age": 20,
            "test_time": datetime.now().isoformat(),
            "questionnaire_scores": {
                "焦虑": 12,
                "抑郁": 8,
                "压力": 15
            },
            "physiological_data_summary": {
                "心率": 85.0,
                "脑电alpha": 13.2
            },
            "ai_summary": "检测结果正常",
            "report_file_path": "reports/test.pdf"
        }
        client.post("/api/test-records/", json=test_data)
        
        response = client.get("/api/client/test-status/T001")
        assert response.status_code == 200
        data = response.json()
        assert data["student_id"] == "T001"
        assert data["status"] == "completed"
        assert data["test_record_count"] == 1

class TestErrorHandling:
    """错误处理测试"""
    
    def test_404_error(self, client):
        """测试404错误"""
        response = client.get("/api/nonexistent-endpoint")
        assert response.status_code == 404
    
    def test_422_error(self, client):
        """测试422错误（数据验证错误）"""
        # 发送无效数据
        invalid_data = {
            "invalid_field": "invalid_value"
        }
        response = client.post("/api/students/", json=invalid_data)
        assert response.status_code == 422
    
    def test_500_error(self, client, db):
        """测试500错误（服务器内部错误）"""
        # 模拟数据库错误
        with pytest.raises(Exception):
            # 这里应该是一个会导致500错误的操作
            pass

if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
