#!/usr/bin/env python3
"""
验收测试脚本
验证系统功能是否符合改造方案要求
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, Any, List
import sys
import os

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'psy_admin_fastapi'))

class AcceptanceTester:
    def __init__(self, base_url: str = "http://localhost:8002"):
        self.base_url = base_url
        self.session = None
        self.token = None
        self.test_results = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def login(self, username: str = "admin", password: str = "admin123"):
        """登录获取token"""
        login_data = {
            "username": username,
            "password": password
        }
        
        async with self.session.post(f"{self.base_url}/token", data=login_data) as response:
            if response.status == 200:
                data = await response.json()
                self.token = data["access_token"]
                return True
            else:
                print(f"登录失败: {response.status}")
                return False
    
    async def make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """发送HTTP请求"""
        headers = kwargs.get('headers', {})
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        kwargs['headers'] = headers
        
        async with self.session.request(method, f"{self.base_url}{endpoint}", **kwargs) as response:
            data = None
            if response.content_type == 'application/json':
                data = await response.json()
            else:
                data = await response.text()
            
            return {
                'status_code': response.status,
                'data': data,
                'success': 200 <= response.status < 300
            }
    
    def record_test(self, test_name: str, success: bool, details: str = ""):
        """记录测试结果"""
        self.test_results.append({
            'test_name': test_name,
            'success': success,
            'details': details,
            'timestamp': time.time()
        })
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
    
    async def test_authentication(self):
        """测试认证功能"""
        print("\n=== 测试认证功能 ===")
        
        # 测试登录
        login_data = {"username": "admin", "password": "admin123"}
        result = await self.make_request('POST', '/token', data=login_data)
        
        if result['success'] and 'access_token' in result['data']:
            self.record_test("用户登录", True, "成功获取访问令牌")
            self.token = result['data']['access_token']
        else:
            self.record_test("用户登录", False, f"登录失败: {result['data']}")
            return False
        
        # 测试受保护接口
        result = await self.make_request('GET', '/users/me/')
        self.record_test("受保护接口访问", result['success'], 
                        "成功" if result['success'] else f"失败: {result['data']}")
        
        return True
    
    async def test_student_management(self):
        """测试学生管理功能"""
        print("\n=== 测试学生管理功能 ===")
        
        # 测试获取学生列表
        result = await self.make_request('GET', '/api/students?limit=10')
        self.record_test("获取学生列表", result['success'], 
                        f"返回 {len(result['data'])} 条记录" if result['success'] else f"失败: {result['data']}")
        
        # 测试学号校验
        if result['success'] and result['data']:
            student_id = result['data'][0]['student_id']
            validate_data = {"student_id": student_id}
            result = await self.make_request('POST', '/api/students/validate', json=validate_data)
            self.record_test("学号校验", result['success'], 
                            "校验成功" if result['success'] else f"校验失败: {result['data']}")
    
    async def test_batch_import(self):
        """测试批量导入功能"""
        print("\n=== 测试批量导入功能 ===")
        
        # 创建测试Excel数据
        import pandas as pd
        from io import BytesIO
        
        test_data = {
            'name': ['测试学生1', '测试学生2'],
            'student_id': ['TEST001', 'TEST002'],
            'class_name': ['测试班级', '测试班级'],
            'gender': ['男', '女']
        }
        df = pd.DataFrame(test_data)
        
        # 转换为Excel字节流
        excel_buffer = BytesIO()
        df.to_excel(excel_buffer, index=False, engine='openpyxl')
        excel_buffer.seek(0)
        
        # 测试批量导入
        data = aiohttp.FormData()
        data.add_field('file', excel_buffer.getvalue(), filename='test_students.xlsx', content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        
        result = await self.make_request('POST', '/api/students/batch-import', data=data)
        
        if result['success']:
            response_data = result['data']
            self.record_test("批量导入", True, 
                           f"成功导入 {response_data.get('success_count', 0)} 条记录")
        else:
            self.record_test("批量导入", False, f"导入失败: {result['data']}")
    
    async def test_test_records(self):
        """测试检测记录功能"""
        print("\n=== 测试检测记录功能 ===")
        
        # 测试获取检测记录列表
        result = await self.make_request('GET', '/test-data/records/?limit=10')
        self.record_test("获取检测记录列表", result['success'], 
                        f"返回 {len(result['data'])} 条记录" if result['success'] else f"失败: {result['data']}")
        
        # 测试获取单个记录详情
        if result['success'] and result['data']:
            record_id = result['data'][0]['id']
            result = await self.make_request('GET', f'/test-data/records/{record_id}')
            self.record_test("获取记录详情", result['success'], 
                            "获取成功" if result['success'] else f"获取失败: {result['data']}")
    
    async def test_dashboard(self):
        """测试仪表板功能"""
        print("\n=== 测试仪表板功能 ===")
        
        # 测试统计数据
        result = await self.make_request('GET', '/api/dashboard/stats')
        if result['success']:
            stats = result['data']
            self.record_test("仪表板统计", True, 
                           f"学生数: {stats.get('total_students', 0)}, "
                           f"记录数: {stats.get('total_records', 0)}")
        else:
            self.record_test("仪表板统计", False, f"获取失败: {result['data']}")
        
        # 测试趋势数据
        result = await self.make_request('GET', '/api/dashboard/trend?days=7')
        self.record_test("趋势数据", result['success'], 
                        f"返回 {len(result['data'].get('dates', []))} 天数据" if result['success'] else f"失败: {result['data']}")
    
    async def test_reports(self):
        """测试报告功能"""
        print("\n=== 测试报告功能 ===")
        
        # 先获取一个学生ID
        result = await self.make_request('GET', '/api/students?limit=1')
        if result['success'] and result['data']:
            student_id = result['data'][0]['student_id']
            
            # 测试报告预览
            result = await self.make_request('GET', f'/api/reports/{student_id}')
            self.record_test("报告预览", result['success'], 
                            "预览成功" if result['success'] else f"预览失败: {result['data']}")
            
            # 测试报告下载
            result = await self.make_request('GET', f'/api/reports/{student_id}/download?format=pdf')
            self.record_test("报告下载", result['success'], 
                            "下载成功" if result['success'] else f"下载失败: {result['data']}")
    
    async def test_client_apis(self):
        """测试客户端对接接口"""
        print("\n=== 测试客户端对接接口 ===")
        
        # 测试学号验证
        validate_data = {"student_id": "TEST001"}
        result = await self.make_request('POST', '/api/client/validate-student', json=validate_data)
        self.record_test("客户端学号验证", result['success'], 
                        "验证成功" if result['success'] else f"验证失败: {result['data']}")
        
        # 测试检测状态查询
        result = await self.make_request('GET', '/api/client/test-status/TEST001')
        self.record_test("检测状态查询", result['success'], 
                        "查询成功" if result['success'] else f"查询失败: {result['data']}")
    
    async def test_cors_security(self):
        """测试CORS和安全配置"""
        print("\n=== 测试CORS和安全配置 ===")
        
        # 测试OPTIONS请求
        result = await self.make_request('OPTIONS', '/api/students')
        self.record_test("CORS预检请求", result['success'], 
                        "CORS配置正确" if result['success'] else "CORS配置问题")
        
        # 测试未授权访问
        # 临时移除token
        original_token = self.token
        self.token = None
        
        result = await self.make_request('GET', '/api/students')
        self.record_test("未授权访问控制", not result['success'], 
                        "正确拒绝未授权访问" if not result['success'] else "安全漏洞：允许未授权访问")
        
        # 恢复token
        self.token = original_token
    
    async def test_performance_requirements(self):
        """测试性能要求"""
        print("\n=== 测试性能要求 ===")
        
        # 测试统计接口响应时间
        start_time = time.time()
        result = await self.make_request('GET', '/api/dashboard/stats')
        end_time = time.time()
        
        response_time = end_time - start_time
        if response_time < 0.5:  # 500ms
            self.record_test("统计接口性能", True, f"响应时间: {response_time:.3f}s (< 500ms)")
        else:
            self.record_test("统计接口性能", False, f"响应时间: {response_time:.3f}s (>= 500ms)")
    
    def print_summary(self):
        """打印测试总结"""
        print("\n" + "="*50)
        print("验收测试总结")
        print("="*50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"总测试数: {total_tests}")
        print(f"通过测试: {passed_tests}")
        print(f"失败测试: {failed_tests}")
        print(f"通过率: {passed_tests/total_tests*100:.1f}%")
        
        if failed_tests > 0:
            print("\n失败的测试:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test_name']}: {result['details']}")
        
        print("\n验收结论:")
        if failed_tests == 0:
            print("✅ 所有测试通过，系统符合改造方案要求")
        elif failed_tests <= 2:
            print("⚠️  大部分测试通过，存在少量问题需要修复")
        else:
            print("❌ 存在多个问题，需要进一步优化")

async def main():
    """主测试函数"""
    print("开始验收测试...")
    
    async with AcceptanceTester() as tester:
        # 登录
        if not await tester.login():
            print("登录失败，无法进行测试")
            return
        
        # 执行各项测试
        await tester.test_authentication()
        await tester.test_student_management()
        await tester.test_batch_import()
        await tester.test_test_records()
        await tester.test_dashboard()
        await tester.test_reports()
        await tester.test_client_apis()
        await tester.test_cors_security()
        await tester.test_performance_requirements()
        
        # 打印总结
        tester.print_summary()

if __name__ == "__main__":
    asyncio.run(main())
