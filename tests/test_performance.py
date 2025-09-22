#!/usr/bin/env python3
"""
性能测试套件
测试系统的性能、并发处理能力和资源使用情况
"""
import pytest
import sys
import os
import time
import threading
import concurrent.futures
from datetime import datetime, timedelta
from typing import List, Dict, Any
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from psy_admin_fastapi.main import app
from psy_admin_fastapi.database import get_db_session
from psy_admin_fastapi.models import Base, Student, Test, Score, PhysiologicalData
from psy_admin_fastapi.crud import create_student, create_test_data
from psy_admin_fastapi.schemas import StudentCreate, TestDataUpload
from psy_admin_fastapi.utils.concurrent import thread_pool, thread_safe_db

# 测试数据库URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_performance.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """覆盖数据库依赖"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db_session] = override_get_db

@pytest.fixture(scope="function")
def db():
    """创建测试数据库会话"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db):
    """创建测试客户端"""
    return TestClient(app)

class TestPerformanceAPI:
    """API性能测试类"""
    
    def test_api_response_time(self, client):
        """测试API响应时间"""
        # 测试学生创建API的响应时间
        start_time = time.time()
        
        student_data = {
            "name": "张三",
            "student_id": "T001",
            "class_name": "计算机1班",
            "gender": "男"
        }
        
        response = client.post("/api/students/", json=student_data)
        end_time = time.time()
        
        assert response.status_code == 200
        response_time = end_time - start_time
        assert response_time < 1.0  # 响应时间应小于1秒
    
    def test_concurrent_api_requests(self, client, db):
        """测试并发API请求"""
        def create_student(student_id: str) -> Dict[str, Any]:
            """创建学生并返回结果"""
            student_data = {
                "name": f"学生{student_id}",
                "student_id": student_id,
                "class_name": "计算机1班",
                "gender": "男"
            }
            
            start_time = time.time()
            response = client.post("/api/students/", json=student_data)
            end_time = time.time()
            
            return {
                "student_id": student_id,
                "status_code": response.status_code,
                "response_time": end_time - start_time,
                "success": response.status_code == 200
            }
        
        # 创建多个并发请求
        student_ids = [f"T{i:03d}" for i in range(50)]
        results = []
        
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_student, student_id) for student_id in student_ids]
            
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                results.append(result)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 验证结果
        successful_requests = sum(1 for r in results if r["success"])
        failed_requests = len(results) - successful_requests
        
        # 验证性能指标
        assert successful_requests >= 45  # 至少90%的请求成功
        assert failed_requests <= 5  # 失败请求不超过5个
        assert total_time < 10.0  # 总时间应小于10秒
        
        # 计算平均响应时间
        avg_response_time = sum(r["response_time"] for r in results) / len(results)
        assert avg_response_time < 0.5  # 平均响应时间应小于0.5秒
    
    def test_large_dataset_api_performance(self, client, db):
        """测试大数据集API性能"""
        # 创建大量学生数据
        students_data = []
        for i in range(100):
            students_data.append({
                "name": f"学生{i}",
                "student_id": f"S{i:03d}",
                "class_name": f"计算机{i%10+1}班",
                "gender": "男" if i % 2 == 0 else "女"
            })
        
        # 批量创建学生
        start_time = time.time()
        
        for student_data in students_data:
            response = client.post("/api/students/", json=student_data)
            assert response.status_code == 200
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 验证性能
        assert total_time < 30.0  # 100个学生创建时间应小于30秒
        assert total_time / len(students_data) < 0.3  # 平均每个学生创建时间应小于0.3秒
        
        # 测试查询性能
        start_time = time.time()
        response = client.get("/api/students/")
        end_time = time.time()
        
        assert response.status_code == 200
        query_time = end_time - start_time
        assert query_time < 1.0  # 查询100个学生应小于1秒

class TestPerformanceDatabase:
    """数据库性能测试类"""
    
    def test_database_insert_performance(self, db):
        """测试数据库插入性能"""
        def create_student_batch(start_idx: int, batch_size: int) -> List[Student]:
            """批量创建学生"""
            students = []
            for i in range(start_idx, start_idx + batch_size):
                student_data = StudentCreate(
                    name=f"学生{i}",
                    student_id=f"S{i:05d}",
                    class_name=f"计算机{i%10+1}班",
                    gender="男" if i % 2 == 0 else "女"
                )
                student = create_student(db, student_data)
                students.append(student)
            return students
        
        # 测试不同批量大小的插入性能
        batch_sizes = [10, 50, 100, 500]
        
        for batch_size in batch_sizes:
            start_time = time.time()
            
            students = create_student_batch(0, batch_size)
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # 验证数据
            assert len(students) == batch_size
            
            # 验证性能
            avg_time_per_student = total_time / batch_size
            print(f"批量大小: {batch_size}, 总时间: {total_time:.2f}s, 平均时间: {avg_time_per_student:.4f}s")
            
            # 清理数据
            for student in students:
                db.delete(student)
            db.commit()
    
    def test_database_query_performance(self, db):
        """测试数据库查询性能"""
        # 创建测试数据
        students = []
        for i in range(1000):
            student_data = StudentCreate(
                name=f"学生{i}",
                student_id=f"S{i:04d}",
                class_name=f"计算机{i%10+1}班",
                gender="男" if i % 2 == 0 else "女"
            )
            student = create_student(db, student_data)
            students.append(student)
            
            # 创建检测记录
            test_data = TestDataUpload(
                user_id=f"S{i:04d}",
                name=f"学生{i}",
                gender="男" if i % 2 == 0 else "女",
                age=20,
                test_time=datetime.now(),
                questionnaire_scores={
                    "焦虑": 10 + i % 10,
                    "抑郁": 5 + i % 10,
                    "压力": 15 + i % 10
                },
                physiological_data_summary={
                    "心率": 80.0 + i,
                    "脑电alpha": 10.0 + i
                },
                ai_summary="检测结果正常",
                report_file_path="reports/test.pdf"
            )
            create_test_data(db, test_data)
        
        # 测试查询性能
        query_tests = [
            ("所有学生", lambda: db.query(Student).all()),
            ("按班级筛选", lambda: db.query(Student).filter(Student.class_name == "计算机1班").all()),
            ("按性别筛选", lambda: db.query(Student).filter(Student.gender == "男").all()),
            ("检测记录", lambda: db.query(Test).filter(Test.user_id.like("S%")).all()),
            ("关联查询", lambda: db.query(Student).join(Test).filter(Test.user_id.like("S%")).all())
        ]
        
        for test_name, query_func in query_tests:
            start_time = time.time()
            result = query_func()
            end_time = time.time()
            
            query_time = end_time - start_time
            print(f"{test_name}: {len(result)} 条记录, 耗时: {query_time:.4f}s")
            
            # 验证性能
            if test_name == "所有学生":
                assert query_time < 0.1  # 1000条学生查询应小于0.1秒
            elif test_name == "按班级筛选":
                assert query_time < 0.05  # 100条记录查询应小于0.05秒
            elif test_name == "按性别筛选":
                assert query_time < 0.05  # 500条记录查询应小于0.05秒
            elif test_name == "检测记录":
                assert query_time < 0.1  # 1000条检测记录查询应小于0.1秒
            elif test_name == "关联查询":
                assert query_time < 0.2  # 关联查询应小于0.2秒
    
    def test_database_transaction_performance(self, db):
        """测试数据库事务性能"""
        def create_student_with_transaction(student_id: int) -> Student:
            """创建学生并提交事务"""
            student_data = StudentCreate(
                name=f"学生{student_id}",
                student_id=f"S{student_id:05d}",
                class_name="计算机1班",
                gender="男"
            )
            return create_student(db, student_data)
        
        # 测试事务性能
        start_time = time.time()
        
        students = []
        for i in range(100):
            student = create_student_with_transaction(i)
            students.append(student)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 验证性能
        assert total_time < 5.0  # 100个学生事务创建应小于5秒
        assert total_time / len(students) < 0.05  # 平均每个学生创建应小于0.05秒
        
        # 清理数据
        for student in students:
            db.delete(student)
        db.commit()

class TestPerformanceConcurrency:
    """并发性能测试类"""
    
    def test_thread_pool_performance(self, db):
        """测试线程池性能"""
        def create_student_in_thread(student_id: int) -> Student:
            """在线程中创建学生"""
            student_data = StudentCreate(
                name=f"学生{student_id}",
                student_id=f"S{student_id:05d}",
                class_name="计算机1班",
                gender="男"
            )
            return create_student(db, student_data)
        
        # 测试不同线程数的性能
        thread_counts = [1, 5, 10, 20]
        student_count = 100
        
        for thread_count in thread_counts:
            start_time = time.time()
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
                futures = [executor.submit(create_student_in_thread, i) for i in range(student_count)]
                
                for future in concurrent.futures.as_completed(futures):
                    student = future.result()
                    assert student is not None
            
            end_time = time.time()
            total_time = end_time - start_time
            
            print(f"线程数: {thread_count}, 学生数: {student_count}, 总时间: {total_time:.2f}s")
            
            # 验证性能
            assert total_time < 10.0  # 总时间应小于10秒
    
    def test_concurrent_database_operations(self, db):
        """测试并发数据库操作"""
        def create_student_batch(batch_id: int, batch_size: int) -> List[Student]:
            """创建一批学生"""
            students = []
            for i in range(batch_size):
                student_data = StudentCreate(
                    name=f"学生{batch_id}_{i}",
                    student_id=f"B{batch_id:03d}_{i:03d}",
                    class_name="计算机1班",
                    gender="男"
                )
                student = create_student(db, student_data)
                students.append(student)
            return students
        
        # 测试并发批处理
        batch_count = 10
        batch_size = 10
        total_students = batch_count * batch_size
        
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(create_student_batch, i, batch_size) for i in range(batch_count)]
            
            all_students = []
            for future in concurrent.futures.as_completed(futures):
                students = future.result()
                all_students.extend(students)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 验证结果
        assert len(all_students) == total_students
        
        # 验证性能
        assert total_time < 5.0  # 总时间应小于5秒
        assert total_time / total_students < 0.01  # 平均每个学生创建应小于0.01秒
        
        # 清理数据
        for student in all_students:
            db.delete(student)
        db.commit()
    
    def test_mixed_concurrent_operations(self, db):
        """测试混合并发操作"""
        def create_student(student_id: int) -> Student:
            """创建学生"""
            student_data = StudentCreate(
                name=f"学生{student_id}",
                student_id=f"S{student_id:05d}",
                class_name="计算机1班",
                gender="男"
            )
            return create_student(db, student_data)
        
        def query_students(student_id: int) -> List[Student]:
            """查询学生"""
            return db.query(Student).filter(Student.student_id.like(f"S{student_id:05d}%")).all()
        
        # 混合创建和查询操作
        operations = []
        for i in range(50):
            if i % 2 == 0:
                operations.append(("create", i))
            else:
                operations.append(("query", i))
        
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            
            for op_type, op_id in operations:
                if op_type == "create":
                    future = executor.submit(create_student, op_id)
                else:
                    future = executor.submit(query_students, op_id)
                futures.append(future)
            
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if isinstance(result, list):
                    assert len(result) >= 0  # 查询结果可以是空的
                else:
                    assert result is not None  # 创建结果应该是学生对象
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 验证性能
        assert total_time < 10.0  # 总时间应小于10秒

class TestPerformanceMemory:
    """内存性能测试类"""
    
    def test_large_dataset_memory_usage(self, db):
        """测试大数据集内存使用"""
        import psutil
        import gc
        
        def get_memory_usage():
            """获取当前内存使用情况"""
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # MB
        
        # 创建大量数据
        memory_before = get_memory_usage()
        
        students = []
        for i in range(1000):
            student_data = StudentCreate(
                name=f"学生{i}",
                student_id=f"S{i:04d}",
                class_name=f"计算机{i%10+1}班",
                gender="男" if i % 2 == 0 else "女"
            )
            student = create_student(db, student_data)
            students.append(student)
            
            # 创建检测记录
            test_data = TestDataUpload(
                user_id=f"S{i:04d}",
                name=f"学生{i}",
                gender="男" if i % 2 == 0 else "女",
                age=20,
                test_time=datetime.now(),
                questionnaire_scores={
                    "焦虑": 10 + i % 10,
                    "抑郁": 5 + i % 10,
                    "压力": 15 + i % 10
                },
                physiological_data_summary={
                    "心率": 80.0 + i,
                    "脑电alpha": 10.0 + i
                },
                ai_summary="检测结果正常",
                report_file_path="reports/test.pdf"
            )
            create_test_data(db, test_data)
        
        memory_after = get_memory_usage()
        memory_increase = memory_after - memory_before
        
        print(f"内存使用情况: 创建前 {memory_before:.2f}MB, 创建后 {memory_after:.2f}MB, 增长 {memory_increase:.2f}MB")
        
        # 验证内存使用
        assert memory_increase < 100.0  # 内存增长应小于100MB
        
        # 清理数据
        for student in students:
            db.delete(student)
        db.commit()
        
        # 强制垃圾回收
        gc.collect()
        
        memory_after_cleanup = get_memory_usage()
        memory_cleanup = memory_after - memory_after_cleanup
        
        print(f"清理后内存: {memory_after_cleanup:.2f}MB, 释放 {memory_cleanup:.2f}MB")
        
        # 验证清理效果
        assert memory_cleanup > 0  # 应该释放内存
    
    def test_memory_leak_detection(self, db):
        """测试内存泄漏检测"""
        import psutil
        import gc
        
        def get_memory_usage():
            """获取当前内存使用情况"""
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # MB
        
        # 创建和销毁大量数据
        iterations = 10
        memory_usages = []
        
        for iteration in range(iterations):
            # 创建数据
            students = []
            for i in range(100):
                student_data = StudentCreate(
                    name=f"学生{iteration}_{i}",
                    student_id=f"S{iteration:02d}_{i:03d}",
                    class_name="计算机1班",
                    gender="男"
                )
                student = create_student(db, student_data)
                students.append(student)
            
            # 模拟使用
            time.sleep(0.1)
            
            # 清理数据
            for student in students:
                db.delete(student)
            db.commit()
            
            # 强制垃圾回收
            gc.collect()
            
            # 记录内存使用
            memory_usage = get_memory_usage()
            memory_usages.append(memory_usage)
            
            print(f"迭代 {iteration + 1}: 内存使用 {memory_usage:.2f}MB")
        
        # 检查内存泄漏
        memory_increase = memory_usages[-1] - memory_usages[0]
        
        print(f"内存增长: {memory_increase:.2f}MB")
        
        # 验证没有内存泄漏
        assert memory_increase < 10.0  # 内存增长应小于10MB

class TestPerformanceStress:
    """压力测试类"""
    
    def test_high_concurrent_requests(self, client, db):
        """测试高并发请求"""
        def make_request(request_id: int) -> Dict[str, Any]:
            """发送API请求"""
            start_time = time.time()
            
            # 随机选择操作类型
            import random
            operation = random.choice(["create", "query"])
            
            if operation == "create":
                student_data = {
                    "name": f"学生{request_id}",
                    "student_id": f"T{request_id:05d}",
                    "class_name": "计算机1班",
                    "gender": "男"
                }
                response = client.post("/api/students/", json=student_data)
            else:
                response = client.get("/api/students/")
            
            end_time = time.time()
            
            return {
                "request_id": request_id,
                "operation": operation,
                "status_code": response.status_code,
                "response_time": end_time - start_time,
                "success": response.status_code == 200
            }
        
        # 模拟高并发场景
        concurrent_users = 50
        requests_per_user = 20
        total_requests = concurrent_users * requests_per_user
        
        print(f"开始压力测试: {concurrent_users} 个并发用户, 每个用户 {requests_per_user} 个请求")
        
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = []
            
            for user_id in range(concurrent_users):
                user_futures = [executor.submit(make_request, user_id * requests_per_user + i) 
                              for i in range(requests_per_user)]
                futures.extend(user_futures)
            
            results = []
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                results.append(result)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 分析结果
        successful_requests = sum(1 for r in results if r["success"])
        failed_requests = len(results) - successful_requests
        avg_response_time = sum(r["response_time"] for r in results) / len(results)
        
        print(f"压力测试结果:")
        print(f"总请求数: {total_requests}")
        print(f"成功请求数: {successful_requests}")
        print(f"失败请求数: {failed_requests}")
        print(f"成功率: {successful_requests / total_requests * 100:.2f}%")
        print(f"总时间: {total_time:.2f}s")
        print(f"平均响应时间: {avg_response_time:.4f}s")
        print(f"每秒请求数: {total_requests / total_time:.2f}")
        
        # 验证性能指标
        assert successful_requests / total_requests >= 0.95  # 成功率应大于95%
        assert avg_response_time < 1.0  # 平均响应时间应小于1秒
        assert total_requests / total_time > 10  # 每秒应能处理超过10个请求
    
    def test_database_stress_test(self, db):
        """测试数据库压力"""
        def create_student_batch(batch_id: int, batch_size: int) -> List[Student]:
            """创建一批学生"""
            students = []
            for i in range(batch_size):
                student_data = StudentCreate(
                    name=f"压力测试学生{batch_id}_{i}",
                    student_id=f"STRESS{batch_id:03d}_{i:04d}",
                    class_name="计算机1班",
                    gender="男"
                )
                student = create_student(db, student_data)
                students.append(student)
            return students
        
        # 模拟数据库压力
        batch_count = 100
        batch_size = 10
        total_students = batch_count * batch_size
        
        print(f"开始数据库压力测试: {batch_count} 个批次, 每批 {batch_size} 个学生")
        
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(create_student_batch, i, batch_size) 
                      for i in range(batch_count)]
            
            all_students = []
            for future in concurrent.futures.as_completed(futures):
                students = future.result()
                all_students.extend(students)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 验证结果
        assert len(all_students) == total_students
        
        # 验证性能
        print(f"数据库压力测试结果:")
        print(f"总学生数: {total_students}")
        print(f"总时间: {total_time:.2f}s")
        print(f"平均每批时间: {total_time / batch_count:.4f}s")
        print(f"平均每个学生时间: {total_time / total_students:.6f}s")
        
        assert total_time < 30.0  # 总时间应小于30秒
        assert total_time / total_students < 0.001  # 平均每个学生创建应小于0.001秒
        
        # 清理数据
        for student in all_students:
            db.delete(student)
        db.commit()

if __name__ == "__main__":
    # 运行性能测试
    pytest.main([__file__, "-v", "--tb=short"])
