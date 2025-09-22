#!/usr/bin/env python3
"""
数据库操作测试套件
"""
import pytest
import sys
import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from psy_admin_fastapi.database import get_db
from psy_admin_fastapi.models import Base, Student, Test, Score, PhysiologicalData, AdminUser
from psy_admin_fastapi.crud import (
    create_student, batch_create_students, update_student, delete_student,
    create_test_data, get_test_records, get_test_record_detail,
    validate_student_for_client, create_client_test_data, get_student_test_status_for_client
)
from psy_admin_fastapi.schemas import StudentCreate, ExcelImportSchema, TestDataUpload, ClientTestDataUpload
from psy_admin_fastapi.security import get_password_hash

# 测试数据库URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_database.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    """创建测试数据库会话"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

class TestStudentOperations:
    """学生操作测试"""
    
    def test_create_student(self, db):
        """测试创建学生"""
        student_data = StudentCreate(
            name="张三",
            student_id="T001",
            class_name="计算机1班",
            gender="男"
        )
        
        result = create_student(db, student_data)
        
        # 验证结果
        assert result.name == "张三"
        assert result.student_id == "T001"
        assert result.class_name == "计算机1班"
        assert result.gender == "男"
        assert result.id is not None
    
    def test_create_duplicate_student(self, db):
        """测试创建重复学号的学生"""
        # 创建第一个学生
        student_data1 = StudentCreate(
            name="张三",
            student_id="T001",
            class_name="计算机1班",
            gender="男"
        )
        create_student(db, student_data1)
        
        # 尝试创建重复学号的学生
        student_data2 = StudentCreate(
            name="李四",
            student_id="T001",  # 重复学号
            class_name="计算机2班",
            gender="女"
        )
        
        # 应该抛出异常
        with pytest.raises(Exception):
            create_student(db, student_data2)
    
    def test_batch_create_students(self, db):
        """测试批量创建学生"""
        students_data = [
            ExcelImportSchema(
                name="学生1",
                student_id="S001",
                class_name="计算机1班",
                gender="男"
            ),
            ExcelImportSchema(
                name="学生2",
                student_id="S002",
                class_name="计算机1班",
                gender="女"
            ),
            ExcelImportSchema(
                name="学生3",
                student_id="S003",
                class_name="计算机2班",
                gender="男"
            )
        ]
        
        results = batch_create_students(db, students_data)
        
        # 验证结果
        assert len(results) == 3
        assert results[0].name == "学生1"
        assert results[0].student_id == "S001"
        assert results[1].name == "学生2"
        assert results[1].student_id == "S002"
        assert results[2].name == "学生3"
        assert results[2].student_id == "S003"
    
    def test_update_student(self, db):
        """测试更新学生信息"""
        # 先创建学生
        student_data = StudentCreate(
            name="张三",
            student_id="T001",
            class_name="计算机1班",
            gender="男"
        )
        student = create_student(db, student_data)
        
        # 更新学生信息
        update_data = StudentCreate(
            name="张三（更新）",
            student_id="T001",
            class_name="计算机1班（更新）",
            gender="男"
        )
        
        result = update_student(db, "T001", update_data)
        
        # 验证更新结果
        assert result.name == "张三（更新）"
        assert result.class_name == "计算机1班（更新）"
        assert result.gender == "男"
        assert result.student_id == "T001"
    
    def test_delete_student(self, db):
        """测试删除学生"""
        # 先创建学生
        student_data = StudentCreate(
            name="张三",
            student_id="T001",
            class_name="计算机1班",
            gender="男"
        )
        student = create_student(db, student_data)
        
        # 删除学生
        result = delete_student(db, "T001")
        
        # 验证删除结果
        assert result == True
        
        # 验证学生已被删除
        deleted_student = db.query(Student).filter(Student.student_id == "T001").first()
        assert deleted_student is None
    
    def test_get_student_with_filters(self, db):
        """测试带筛选条件的学生查询"""
        # 创建多个学生
        students_data = [
            StudentCreate(name="学生1", student_id="S001", class_name="计算机1班", gender="男"),
            StudentCreate(name="学生2", student_id="S002", class_name="计算机1班", gender="女"),
            StudentCreate(name="学生3", student_id="S003", class_name="计算机2班", gender="男"),
        ]
        
        for student_data in students_data:
            create_student(db, student_data)
        
        # 测试按班级筛选
        class1_students = db.query(Student).filter(Student.class_name == "计算机1班").all()
        assert len(class1_students) == 2
        
        # 测试按性别筛选
        male_students = db.query(Student).filter(Student.gender == "男").all()
        assert len(male_students) == 2

class TestTestRecordOperations:
    """检测记录操作测试"""
    
    def test_create_test_data(self, db):
        """测试创建检测数据"""
        # 先创建学生
        student_data = StudentCreate(
            name="张三",
            student_id="T001",
            class_name="计算机1班",
            gender="男"
        )
        student = create_student(db, student_data)
        
        # 创建检测数据
        test_data = TestDataUpload(
            user_id="T001",
            name="张三",
            gender="男",
            age=20,
            test_time=datetime.now(),
            questionnaire_scores={
                "焦虑": 12,
                "抑郁": 8,
                "压力": 15
            },
            physiological_data_summary={
                "心率": 85.0,
                "脑电alpha": 13.2
            },
            ai_summary="检测结果正常",
            report_file_path="reports/test.pdf"
        )
        
        result = create_test_data(db, test_data)
        
        # 验证结果
        assert result.student_fk_id == student.id
        assert result.is_abnormal == False
        assert result.status == "pending"
        assert result.ai_summary == "检测结果正常"
        assert result.id is not None
        
        # 验证关联数据
        scores = db.query(Score).filter(Score.test_fk_id == result.id).all()
        assert len(scores) == 3
        
        phys_data = db.query(PhysiologicalData).filter(PhysiologicalData.test_fk_id == result.id).all()
        assert len(phys_data) == 2
    
    def test_create_abnormal_test_data(self, db):
        """测试创建异常检测数据"""
        # 先创建学生
        student_data = StudentCreate(
            name="张三",
            student_id="T001",
            class_name="计算机1班",
            gender="男"
        )
        student = create_student(db, student_data)
        
        # 创建异常检测数据
        test_data = TestDataUpload(
            user_id="T001",
            name="张三",
            gender="男",
            age=20,
            test_time=datetime.now(),
            questionnaire_scores={
                "焦虑": 18,  # 超过阈值
                "抑郁": 8,
                "压力": 12
            },
            physiological_data_summary={
                "心率": 85.0,
                "脑电alpha": 13.2
            },
            ai_summary="检测结果异常",
            report_file_path="reports/test.pdf"
        )
        
        result = create_test_data(db, test_data)
        
        # 验证结果
        assert result.is_abnormal == True
        assert "焦虑" in result.ai_summary  # AI总结应该包含异常模块信息
    
    def test_get_test_records(self, db):
        """测试获取检测记录列表"""
        # 创建学生和检测数据
        student_data = StudentCreate(
            name="张三",
            student_id="T001",
            class_name="计算机1班",
            gender="男"
        )
        student = create_student(db, student_data)
        
        test_data = TestDataUpload(
            user_id="T001",
            name="张三",
            gender="男",
            age=20,
            test_time=datetime.now(),
            questionnaire_scores={
                "焦虑": 12,
                "抑郁": 8,
                "压力": 15
            },
            physiological_data_summary={
                "心率": 85.0,
                "脑电alpha": 13.2
            },
            ai_summary="检测结果正常",
            report_file_path="reports/test.pdf"
        )
        
        create_test_data(db, test_data)
        
        # 获取检测记录
        records = get_test_records(db)
        
        # 验证结果
        assert len(records) == 1
        assert records[0].student_fk_id == student.id
        assert records[0].is_abnormal == False
    
    def test_get_test_record_detail(self, db):
        """测试获取检测记录详情"""
        # 创建学生和检测数据
        student_data = StudentCreate(
            name="张三",
            student_id="T001",
            class_name="计算机1班",
            gender="男"
        )
        student = create_student(db, student_data)
        
        test_data = TestDataUpload(
            user_id="T001",
            name="张三",
            gender="男",
            age=20,
            test_time=datetime.now(),
            questionnaire_scores={
                "焦虑": 12,
                "抑郁": 8,
                "压力": 15
            },
            physiological_data_summary={
                "心率": 85.0,
                "脑电alpha": 13.2
            },
            ai_summary="检测结果正常",
            report_file_path="reports/test.pdf"
        )
        
        test_record = create_test_data(db, test_data)
        
        # 获取检测记录详情
        detail = get_test_record_detail(db, test_record.id)
        
        # 验证结果
        assert detail.id == test_record.id
        assert detail.student.name == "张三"
        assert detail.student.student_id == "T001"
        assert len(detail.scores) == 3
        assert len(detail.physiological_data) == 2
    
    def test_get_test_records_with_filters(self, db):
        """测试带筛选条件的检测记录查询"""
        # 创建学生和正常检测数据
        student_data = StudentCreate(
            name="张三",
            student_id="T001",
            class_name="计算机1班",
            gender="男"
        )
        student = create_student(db, student_data)
        
        normal_test_data = TestDataUpload(
            user_id="T001",
            name="张三",
            gender="男",
            age=20,
            test_time=datetime.now(),
            questionnaire_scores={
                "焦虑": 12,
                "抑郁": 8,
                "压力": 15
            },
            physiological_data_summary={
                "心率": 85.0,
                "脑电alpha": 13.2
            },
            ai_summary="检测结果正常",
            report_file_path="reports/test.pdf"
        )
        
        # 创建异常检测数据
        abnormal_test_data = TestDataUpload(
            user_id="T001",
            name="张三",
            gender="男",
            age=20,
            test_time=datetime.now(),
            questionnaire_scores={
                "焦虑": 18,  # 异常
                "抑郁": 8,
                "压力": 12
            },
            physiological_data_summary={
                "心率": 85.0,
                "脑电alpha": 13.2
            },
            ai_summary="检测结果异常",
            report_file_path="reports/test.pdf"
        )
        
        create_test_data(db, normal_test_data)
        create_test_data(db, abnormal_test_data)
        
        # 测试按异常状态筛选
        abnormal_records = get_test_records(db, is_abnormal=True)
        assert len(abnormal_records) == 1
        assert abnormal_records[0].is_abnormal == True
        
        # 测试按正常状态筛选
        normal_records = get_test_records(db, is_abnormal=False)
        assert len(normal_records) == 1
        assert normal_records[0].is_abnormal == False

class TestClientOperations:
    """客户端操作测试"""
    
    def test_validate_student_success(self, db):
        """测试学号验证成功"""
        # 创建学生
        student_data = StudentCreate(
            name="张三",
            student_id="T001",
            class_name="计算机1班",
            gender="男"
        )
        create_student(db, student_data)
        
        # 验证学号
        result = validate_student_for_client(db, "T001")
        
        # 验证结果
        assert result["exists"] == True
        assert result["student_info"]["name"] == "张三"
        assert result["student_info"]["student_id"] == "T001"
        assert result["student_info"]["class_name"] == "计算机1班"
        assert result["student_info"]["gender"] == "男"
    
    def test_validate_student_failure(self, db):
        """测试学号验证失败"""
        # 验证不存在的学号
        result = validate_student_for_client(db, "NONEXISTENT")
        
        # 验证结果
        assert result["exists"] == False
        assert result["student_info"] is None
    
    def test_create_client_test_data(self, db):
        """测试创建客户端检测数据"""
        # 创建客户端检测数据
        test_data = ClientTestDataUpload(
            user_id="T001",
            name="张三",
            gender="男",
            age=20,
            test_time=datetime.now(),
            questionnaire_scores={
                "焦虑": 18,  # 异常
                "抑郁": 8,
                "压力": 12
            },
            physiological_data_summary={
                "心率": 85.0,
                "脑电alpha": 13.2
            },
            ai_summary="检测结果异常",
            report_file_path="reports/client_test.pdf"
        )
        
        result = create_client_test_data(db, test_data)
        
        # 验证结果
        assert result.is_abnormal == True
        assert result.status == "completed"  # 客户端数据默认为已完成状态
        
        # 验证学生被自动创建
        student = db.query(Student).filter(Student.student_id == "T001").first()
        assert student.name == "张三"
        assert student.student_id == "T001"
    
    def test_get_student_test_status(self, db):
        """测试获取学生检测状态"""
        # 创建学生和检测数据
        student_data = StudentCreate(
            name="张三",
            student_id="T001",
            class_name="计算机1班",
            gender="男"
        )
        student = create_student(db, student_data)
        
        test_data = ClientTestDataUpload(
            user_id="T001",
            name="张三",
            gender="男",
            age=20,
            test_time=datetime.now(),
            questionnaire_scores={
                "焦虑": 12,
                "抑郁": 8,
                "压力": 15
            },
            physiological_data_summary={
                "心率": 85.0,
                "脑电alpha": 13.2
            },
            ai_summary="检测结果正常",
            report_file_path="reports/test.pdf"
        )
        
        create_client_test_data(db, test_data)
        
        # 获取学生检测状态
        status = get_student_test_status_for_client(db, "T001")
        
        # 验证结果
        assert status["student_id"] == "T001"
        assert status["status"] == "completed"
        assert status["is_abnormal"] == False
        assert status["test_record_count"] == 1

class TestDatabaseIntegrity:
    """数据库完整性测试"""
    
    def test_foreign_key_constraints(self, db):
        """测试外键约束"""
        # 创建检测数据但不创建学生（应该失败）
        test_data = TestDataUpload(
            user_id="NONEXISTENT",
            name="不存在的学生",
            gender="男",
            age=20,
            test_time=datetime.now(),
            questionnaire_scores={
                "焦虑": 12,
                "抑郁": 8,
                "压力": 15
            },
            physiological_data_summary={
                "心率": 85.0,
                "脑电alpha": 13.2
            },
            ai_summary="检测结果",
            report_file_path="reports/test.pdf"
        )
        
        # 应该自动创建学生
        result = create_test_data(db, test_data)
        assert result is not None
        
        # 验证学生被创建
        student = db.query(Student).filter(Student.student_id == "NONEXISTENT").first()
        assert student is not None
    
    def test_data_consistency(self, db):
        """测试数据一致性"""
        # 创建学生和检测数据
        student_data = StudentCreate(
            name="张三",
            student_id="T001",
            class_name="计算机1班",
            gender="男"
        )
        student = create_student(db, student_data)
        
        test_data = TestDataUpload(
            user_id="T001",
            name="张三",
            gender="男",
            age=20,
            test_time=datetime.now(),
            questionnaire_scores={
                "焦虑": 12,
                "抑郁": 8,
                "压力": 15
            },
            physiological_data_summary={
                "心率": 85.0,
                "脑电alpha": 13.2
            },
            ai_summary="检测结果正常",
            report_file_path="reports/test.pdf"
        )
        
        test_record = create_test_data(db, test_data)
        
        # 验证数据一致性
        # 1. 检测记录关联的学生ID应该正确
        assert test_record.student_fk_id == student.id
        
        # 2. 问卷得分应该关联到正确的检测记录
        scores = db.query(Score).filter(Score.test_fk_id == test_record.id).all()
        for score in scores:
            assert score.test_fk_id == test_record.id
        
        # 3. 生理数据应该关联到正确的检测记录
        phys_data = db.query(PhysiologicalData).filter(PhysiologicalData.test_fk_id == test_record.id).all()
        for data in phys_data:
            assert data.test_fk_id == test_record.id
    
    def test_transaction_rollback(self, db):
        """测试事务回滚"""
        # 获取初始学生数量
        initial_count = db.query(Student).count()
        
        # 开始事务
        try:
            # 创建学生
            student_data = StudentCreate(
                name="张三",
                student_id="T001",
                class_name="计算机1班",
                gender="男"
            )
            create_student(db, student_data)
            
            # 创建检测数据
            test_data = TestDataUpload(
                user_id="T001",
                name="张三",
                gender="男",
                age=20,
                test_time=datetime.now(),
                questionnaire_scores={
                    "焦虑": 12,
                    "抑郁": 8,
                    "压力": 15
                },
                physiological_data_summary={
                    "心率": 85.0,
                    "脑电alpha": 13.2
                },
                ai_summary="检测结果正常",
                report_file_path="reports/test.pdf"
            )
            create_test_data(db, test_data)
            
            # 模拟错误，触发回滚
            raise Exception("模拟错误")
            
        except Exception as e:
            # 回滚事务
            db.rollback()
        
        # 验证数据没有被提交
        final_count = db.query(Student).count()
        assert final_count == initial_count

if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
