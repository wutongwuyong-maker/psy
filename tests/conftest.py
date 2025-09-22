#!/usr/bin/env python3
"""
测试配置文件
配置测试环境、测试数据和测试参数
"""
import pytest
import sys
import os
import tempfile
import shutil
from datetime import datetime, timezone
from typing import Dict, Any, List
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from psy_admin_fastapi.main import app
from psy_admin_fastapi.database import get_db_session, get_db
from psy_admin_fastapi.models import Base, Student, Test, Score, PhysiologicalData, AdminUser
from psy_admin_fastapi.crud import create_student, create_test_data
from psy_admin_fastapi.schemas import StudentCreate, TestDataUpload
from psy_admin_fastapi.security import get_password_hash

# 测试配置
TEST_CONFIG = {
    "database": {
        "url": "sqlite:///./test.db",
        "echo": False
    },
    "api": {
        "base_url": "http://localhost:8000",
        "timeout": 30,
        "max_retries": 3
    },
    "performance": {
        "concurrent_users": 50,
        "requests_per_user": 20,
        "batch_size": 100
    },
    "data": {
        "student_count": 1000,
        "test_record_count": 5000,
        "anomaly_rate": 0.1
    }
}

@pytest.fixture(scope="session")
def test_config():
    """返回测试配置"""
    return TEST_CONFIG

@pytest.fixture(scope="session")
def temp_dir():
    """创建临时目录"""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path)

@pytest.fixture(scope="session")
def test_db_url(test_config, temp_dir):
    """创建测试数据库URL"""
    db_path = os.path.join(temp_dir, "test.db")
    return f"sqlite:///{db_path}"

@pytest.fixture(scope="session")
def engine(test_db_url):
    """创建测试数据库引擎"""
    return create_engine(test_db_url, echo=False)

@pytest.fixture(scope="session")
def SessionLocal(engine):
    """创建测试数据库会话工厂"""
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db(engine, SessionLocal):
    """创建测试数据库会话"""
    # 创建表
    Base.metadata.create_all(bind=engine)
    
    # 创建会话
    db = SessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        # 清理表
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    """创建测试客户端"""
    # 覆盖数据库依赖
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db_session] = override_get_db
    
    return TestClient(app)

@pytest.fixture
def test_students(db):
    """创建测试学生数据"""
    students = []
    
    # 创建标准学生
    standard_students = [
        {"name": "张三", "student_id": "T001", "class_name": "计算机1班", "gender": "男"},
        {"name": "李四", "student_id": "T002", "class_name": "计算机1班", "gender": "女"},
        {"name": "王五", "student_id": "T003", "class_name": "计算机2班", "gender": "男"},
        {"name": "赵六", "student_id": "T004", "class_name": "计算机2班", "gender": "女"},
    ]
    
    for student_data in standard_students:
        student = create_student(db, StudentCreate(**student_data))
        students.append(student)
    
    # 创建批量学生
    for i in range(10):
        student_data = StudentCreate(
            name=f"批量学生{i}",
            student_id=f"B{i:03d}",
            class_name=f"计算机{i%5+1}班",
            gender="男" if i % 2 == 0 else "女"
        )
        student = create_student(db, student_data)
        students.append(student)
    
    return students

@pytest.fixture
def test_admin_user(db):
    """创建测试管理员用户"""
    admin_user = AdminUser(
        username="test_admin",
        hashed_password=get_password_hash("test_password")
    )
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    return admin_user

@pytest.fixture
def test_test_records(db, test_students):
    """创建测试检测记录"""
    test_records = []
    
    for i, student in enumerate(test_students):
        test_data = TestDataUpload(
            user_id=student.student_id,
            name=student.name,
            gender=student.gender,
            age=20,
            test_time=datetime.now(timezone.utc),
            questionnaire_scores={
                "焦虑": 10 + (i % 10),
                "抑郁": 5 + (i % 8),
                "压力": 15 + (i % 6)
            },
            physiological_data_summary={
                "心率": 80.0 + (i % 20),
                "脑电alpha": 10.0 + (i % 15)
            },
            ai_summary="检测结果正常",
            report_file_path="reports/test.pdf"
        )
        test_record = create_test_data(db, test_data)
        test_records.append(test_record)
    
    return test_records

@pytest.fixture
def test_anomaly_records(db, test_students):
    """创建异常检测记录"""
    anomaly_records = []
    
    # 创建异常记录
    for i, student in enumerate(test_students[:5]):
        test_data = TestDataUpload(
            user_id=student.student_id,
            name=student.name,
            gender=student.gender,
            age=20,
            test_time=datetime.now(timezone.utc),
            questionnaire_scores={
                "焦虑": 25,  # 高分
                "抑郁": 20,  # 高分
                "压力": 22   # 高分
            },
            physiological_data_summary={
                "心率": 120.0,  # 高心率
                "脑电alpha": 5.0  # 低脑电
            },
            ai_summary="检测结果异常，建议关注",
            report_file_path="reports/anomaly_test.pdf"
        )
        test_record = create_test_data(db, test_data)
        anomaly_records.append(test_record)
    
    return anomaly_records

@pytest.fixture
def mock_external_services():
    """模拟外部服务"""
    with patch('psy_admin_fastapi.services.report_service.generate_pdf_report') as mock_pdf, \
         patch('psy_admin_fastapi.services.report_service.generate_excel_report') as mock_excel, \
         patch('psy_admin_fastapi.services.report_service.generate_report_content') as mock_content:
        
        # 设置模拟返回值
        mock_pdf.return_value = "reports/test.pdf"
        mock_excel.return_value = "reports/test.xlsx"
        mock_content.return_value = "测试报告内容"
        
        yield {
            'pdf_generator': mock_pdf,
            'excel_generator': mock_excel,
            'content_generator': mock_content
        }

@pytest.fixture
def mock_database_operations():
    """模拟数据库操作"""
    with patch('psy_admin_fastapi.crud.create_student') as mock_create, \
         patch('psy_admin_fastapi.crud.get_student') as mock_get, \
         patch('psy_admin_fastapi.crud.update_student') as mock_update, \
         patch('psy_admin_fastapi.crud.delete_student') as mock_delete, \
         patch('psy_admin_fastapi.crud.create_test_data') as mock_create_test:
        
        # 设置模拟返回值
        mock_create.return_value = Student(
            id=1,
            name="测试学生",
            student_id="TEST001",
            class_name="测试班级",
            gender="男"
        )
        mock_get.return_value = Student(
            id=1,
            name="测试学生",
            student_id="TEST001",
            class_name="测试班级",
            gender="男"
        )
        mock_update.return_value = Student(
            id=1,
            name="测试学生（更新）",
            student_id="TEST001",
            class_name="测试班级（更新）",
            gender="男"
        )
        mock_delete.return_value = True
        mock_create_test.return_value = Test(
            id=1,
            student_fk_id=1,
            test_time=datetime.now(timezone.utc),
            ai_summary="测试AI总结",
            report_file_path="reports/test.pdf",
            is_abnormal=False,
            status="completed"
        )
        
        yield {
            'create_student': mock_create,
            'get_student': mock_get,
            'update_student': mock_update,
            'delete_student': mock_delete,
            'create_test_data': mock_create_test
        }

@pytest.fixture
def mock_external_apis():
    """模拟外部API"""
    with patch('requests.post') as mock_post, \
         patch('requests.get') as mock_get, \
         patch('requests.put') as mock_put:
        
        # 设置模拟返回值
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_post.return_value = mock_response
        mock_get.return_value = mock_response
        mock_put.return_value = mock_response
        
        yield {
            'post': mock_post,
            'get': mock_get,
            'put': mock_put
        }

@pytest.fixture
def performance_metrics():
    """性能指标收集器"""
    metrics = {
        'response_times': [],
        'throughput': [],
        'error_rates': [],
        'memory_usage': [],
        'cpu_usage': []
    }
    
    yield metrics
    
    # 输出性能指标
    print("\n=== 性能指标汇总 ===")
    if metrics['response_times']:
        avg_response_time = sum(metrics['response_times']) / len(metrics['response_times'])
        print(f"平均响应时间: {avg_response_time:.4f}s")
    
    if metrics['throughput']:
        avg_throughput = sum(metrics['throughput']) / len(metrics['throughput'])
        print(f"平均吞吐量: {avg_throughput:.2f} requests/s")
    
    if metrics['error_rates']:
        avg_error_rate = sum(metrics['error_rates']) / len(metrics['error_rates'])
        print(f"平均错误率: {avg_error_rate:.2f}%")

@pytest.fixture
def test_data_generator():
    """测试数据生成器"""
    def generate_student_data(count: int = 1) -> List[Dict[str, Any]]:
        """生成学生数据"""
        students = []
        for i in range(count):
            students.append({
                "name": f"测试学生{i}",
                "student_id": f"TEST{i:04d}",
                "class_name": f"计算机{i%10+1}班",
                "gender": "男" if i % 2 == 0 else "女"
            })
        return students
    
    def generate_test_data(student_id: str, anomaly: bool = False) -> Dict[str, Any]:
        """生成检测数据"""
        if anomaly:
            return {
                "user_id": student_id,
                "name": f"异常学生{student_id}",
                "gender": "男",
                "age": 20,
                "test_time": datetime.now(timezone.utc),
                "questionnaire_scores": {
                    "焦虑": 25,
                    "抑郁": 20,
                    "压力": 22
                },
                "physiological_data_summary": {
                    "心率": 120.0,
                    "脑电alpha": 5.0
                },
                "ai_summary": "检测结果异常，建议关注",
                "report_file_path": "reports/anomaly_test.pdf"
            }
        else:
            return {
                "user_id": student_id,
                "name": f"正常学生{student_id}",
                "gender": "男",
                "age": 20,
                "test_time": datetime.now(timezone.utc),
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
    
    def generate_large_dataset(count: int) -> List[Dict[str, Any]]:
        """生成大数据集"""
        return generate_student_data(count)
    
    return {
        'generate_student_data': generate_student_data,
        'generate_test_data': generate_test_data,
        'generate_large_dataset': generate_large_dataset
    }

@pytest.fixture
def test_report_generator():
    """测试报告生成器"""
    def generate_pdf_report(content: str, student_id: str) -> str:
        """生成PDF报告"""
        return f"reports/{student_id}_report.pdf"
    
    def generate_excel_report(db, student_id: str) -> str:
        """生成Excel报告"""
        return f"reports/{student_id}_report.xlsx"
    
    def generate_report_content(db, student_id: str) -> str:
        """生成报告内容"""
        return f"学生{student_id}的心理健康检测报告"
    
    return {
        'generate_pdf_report': generate_pdf_report,
        'generate_excel_report': generate_excel_report,
        'generate_report_content': generate_report_content
}

@pytest.fixture
def stress_test_config():
    """压力测试配置"""
    return {
        "concurrent_levels": [10, 25, 50, 100],
        "ramp_up_time": 30,  # 秒
        "test_duration": 60,  # 秒
        "think_time": 1,  # 秒
        "timeout": 30  # 秒
    }

@pytest.fixture
def load_test_config():
    """负载测试配置"""
    return {
        "user_profiles": [
            {
                "name": "轻量用户",
                "think_time_range": (1, 3),
                "operations": ["query"],
                "weight": 0.3
            },
            {
                "name": "中等用户",
                "think_time_range": (2, 5),
                "operations": ["query", "create"],
                "weight": 0.5
            },
            {
                "name": "重度用户",
                "think_time_range": (3, 8),
                "operations": ["query", "create", "update"],
                "weight": 0.2
            }
        ],
        "test_phases": [
            {"duration": 60, "users": 10, "ramp_up": 10},
            {"duration": 120, "users": 50, "ramp_up": 30},
            {"duration": 60, "users": 100, "ramp_up": 20},
            {"duration": 60, "users": 50, "ramp_up": 30}
        ]
    }

@pytest.fixture
def benchmark_config():
    """基准测试配置"""
    return {
        "test_scenarios": [
            {
                "name": "单用户基准测试",
                "concurrent_users": 1,
                "requests_per_user": 100,
                "operations": ["create", "query", "update", "delete"]
            },
            {
                "name": "多用户基准测试",
                "concurrent_users": 10,
                "requests_per_user": 50,
                "operations": ["create", "query", "update", "delete"]
            },
            {
                "name": "高并发基准测试",
                "concurrent_users": 50,
                "requests_per_user": 20,
                "operations": ["create", "query", "update", "delete"]
            }
        ],
        "metrics": [
            "response_time",
            "throughput",
            "error_rate",
            "cpu_usage",
            "memory_usage",
            "disk_io"
        ]
    }

# 测试标记
pytest.mark.performance = pytest.mark.performance
pytest.mark.stress = pytest.mark.stress
pytest.mark.load = pytest.mark.load
pytest.mark.benchmark = pytest.mark.benchmark
pytest.mark.integration = pytest.mark.integration
pytest.mark.unit = pytest.mark.unit

# 自定义断言
def assert_performance(response_time: float, threshold: float = 1.0):
    """断言性能指标"""
    assert response_time < threshold, f"响应时间 {response_time}s 超过阈值 {threshold}s"

def assert_throughput(throughput: float, threshold: float = 10.0):
    """断言吞吐量"""
    assert throughput > threshold, f"吞吐量 {throughput} requests/s 低于阈值 {threshold} requests/s"

def assert_error_rate(error_rate: float, threshold: float = 0.05):
    """断言错误率"""
    assert error_rate < threshold, f"错误率 {error_rate*100}% 超过阈值 {threshold*100}%"

def assert_memory_usage(memory_usage: float, threshold: float = 100.0):
    """断言内存使用"""
    assert memory_usage < threshold, f"内存使用 {memory_usage}MB 超过阈值 {threshold}MB"

# 测试辅助函数
def create_test_student(db, student_data: Dict[str, Any]) -> Student:
    """创建测试学生"""
    return create_student(db, StudentCreate(**student_data))

def create_test_test_record(db, test_data: Dict[str, Any]) -> Test:
    """创建测试检测记录"""
    return create_test_data(db, TestDataUpload(**test_data))

def generate_test_token() -> str:
    """生成测试令牌"""
    import jwt
    from datetime import datetime, timezone, timedelta
    
    payload = {
        "sub": "test_user",
        "exp": datetime.now(timezone.utc) + timedelta(hours=1)
    }
    
    return jwt.encode(payload, "test_secret", algorithm="HS256")

def mock_external_api_response(status_code: int = 200, data: Dict[str, Any] = None):
    """模拟外部API响应"""
    mock_response = Mock()
    mock_response.status_code = status_code
    mock_response.json.return_value = data or {"success": True}
    return mock_response

# 测试夹具注册
def pytest_configure(config):
    """配置pytest"""
    config.addinivalue_line(
        "markers", "performance: 标记性能测试"
    )
    config.addinivalue_line(
        "markers", "stress: 标记压力测试"
    )
    config.addinivalue_line(
        "markers", "load: 标记负载测试"
    )
    config.addinivalue_line(
        "markers", "benchmark: 标记基准测试"
    )
    config.addinivalue_line(
        "markers", "integration: 标记集成测试"
    )
    config.addinivalue_line(
        "markers", "unit: 标记单元测试"
    )

# 测试钩子
def pytest_runtest_setup(item):
    """测试运行前设置"""
    # 检查测试标记
    if "performance" in item.keywords:
        print(f"开始性能测试: {item.name}")
    elif "stress" in item.keywords:
        print(f"开始压力测试: {item.name}")
    elif "load" in item.keywords:
        print(f"开始负载测试: {item.name}")
    elif "benchmark" in item.keywords:
        print(f"开始基准测试: {item.name}")

def pytest_runtest_teardown(item, nextitem):
    """测试运行后清理"""
    # 清理测试数据
    if hasattr(item, 'fixturenames'):
        if 'db' in item.fixturenames:
            # 清理数据库
            pass
