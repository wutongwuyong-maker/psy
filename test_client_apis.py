#!/usr/bin/env python3
"""
测试客户端对接接口的脚本
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8002"

def test_validate_student():
    """测试学号验证接口"""
    print("=== 测试学号验证接口 ===")
    
    # 测试存在的学生
    payload = {
        "student_id": "U001"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/client/validate-student", json=payload)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    print()

def test_upload_test_data():
    """测试检测数据上传接口"""
    print("=== 测试检测数据上传接口 ===")
    
    # 创建一个简单的PDF文件用于测试
    import tempfile
    import os
    
    # 创建临时PDF文件
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.pdf', delete=False) as temp_pdf:
        temp_pdf.write(b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n")
        temp_pdf_path = temp_pdf.name
    
    try:
        # 准备测试数据
        test_data = {
            "student_id": "U001",
            "name": "张三",
            "gender": "男",
            "age": 20,
            "test_time": datetime.now().isoformat(),
            "questionnaire_scores": {
                "焦虑": 8,
                "抑郁": 4,
                "压力": 12
            },
            "physiological_data_summary": {
                "心率": 85,
                "脑电alpha": 13.2
            },
            "ai_summary": "检测出高焦虑风险，建议进一步评估",
            "report_file_path": "pdfs/U001_0710.pdf"
        }
        
        # 准备文件上传
        with open(temp_pdf_path, 'rb') as pdf_file:
            files = {
                'pdf_file': ('test.pdf', pdf_file, 'application/pdf')
            }
            # FastAPI 期望 form-data 格式，test_data 需要作为表单字段
            form_data = {
                'test_data': json.dumps(test_data)
            }
            
            response = requests.post(f"{BASE_URL}/api/client/upload-test-data", files=files, data=form_data)
            print(f"状态码: {response.status_code}")
            if response.status_code == 200:
                print(f"响应: {response.json()}")
            else:
                print(f"错误响应: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    finally:
        # 清理临时文件
        if os.path.exists(temp_pdf_path):
            os.unlink(temp_pdf_path)
    
    print()

def test_get_test_status():
    """测试检测状态查询接口"""
    print("=== 测试检测状态查询接口 ===")
    
    student_id = "U001"
    
    try:
        response = requests.get(f"{BASE_URL}/api/client/test-status/{student_id}")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    print()

if __name__ == "__main__":
    print("开始测试客户端对接接口...")
    print("请确保后端服务器正在运行在 http://localhost:8002")
    print()
    
    test_validate_student()
    test_upload_test_data()
    test_get_test_status()
    
    print("测试完成！")
