#!/usr/bin/env python3
"""
性能测试脚本
用于验证系统性能和压力测试
"""

import asyncio
import aiohttp
import time
import statistics
import json
from typing import List, Dict, Any
import sys
import os

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'psy_admin_fastapi'))

class PerformanceTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        self.token = None
        
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
        """发送HTTP请求并记录性能数据"""
        headers = kwargs.get('headers', {})
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        kwargs['headers'] = headers
        
        start_time = time.time()
        try:
            async with self.session.request(method, f"{self.base_url}{endpoint}", **kwargs) as response:
                end_time = time.time()
                response_time = end_time - start_time
                
                data = None
                if response.content_type == 'application/json':
                    data = await response.json()
                else:
                    data = await response.text()
                
                return {
                    'status_code': response.status,
                    'response_time': response_time,
                    'data': data,
                    'success': 200 <= response.status < 300
                }
        except Exception as e:
            end_time = time.time()
            return {
                'status_code': 0,
                'response_time': end_time - start_time,
                'data': None,
                'success': False,
                'error': str(e)
            }
    
    async def test_dashboard_stats(self, iterations: int = 10) -> Dict[str, Any]:
        """测试仪表板统计接口性能"""
        print(f"测试仪表板统计接口 ({iterations} 次请求)...")
        
        results = []
        for i in range(iterations):
            result = await self.make_request('GET', '/api/dashboard/stats')
            results.append(result)
            if i % 5 == 0:
                print(f"  完成 {i+1}/{iterations} 次请求")
        
        return self._analyze_results(results, "仪表板统计")
    
    async def test_student_list(self, iterations: int = 10) -> Dict[str, Any]:
        """测试学生列表接口性能"""
        print(f"测试学生列表接口 ({iterations} 次请求)...")
        
        results = []
        for i in range(iterations):
            result = await self.make_request('GET', '/api/students?limit=100')
            results.append(result)
            if i % 5 == 0:
                print(f"  完成 {i+1}/{iterations} 次请求")
        
        return self._analyze_results(results, "学生列表")
    
    async def test_test_records(self, iterations: int = 10) -> Dict[str, Any]:
        """测试检测记录接口性能"""
        print(f"测试检测记录接口 ({iterations} 次请求)...")
        
        results = []
        for i in range(iterations):
            result = await self.make_request('GET', '/test-data/records/?limit=100')
            results.append(result)
            if i % 5 == 0:
                print(f"  完成 {i+1}/{iterations} 次请求")
        
        return self._analyze_results(results, "检测记录")
    
    async def test_concurrent_requests(self, endpoint: str, concurrent_users: int = 50, requests_per_user: int = 10) -> Dict[str, Any]:
        """并发压力测试"""
        print(f"并发压力测试: {concurrent_users} 用户，每用户 {requests_per_user} 请求")
        
        async def user_session():
            user_results = []
            for _ in range(requests_per_user):
                result = await self.make_request('GET', endpoint)
                user_results.append(result)
            return user_results
        
        # 创建并发任务
        tasks = [user_session() for _ in range(concurrent_users)]
        
        start_time = time.time()
        all_results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # 展平结果
        results = []
        for user_results in all_results:
            results.extend(user_results)
        
        total_time = end_time - start_time
        total_requests = len(results)
        rps = total_requests / total_time if total_time > 0 else 0
        
        analysis = self._analyze_results(results, f"并发测试({concurrent_users}用户)")
        analysis['total_time'] = total_time
        analysis['requests_per_second'] = rps
        analysis['concurrent_users'] = concurrent_users
        
        return analysis
    
    def _analyze_results(self, results: List[Dict[str, Any]], test_name: str) -> Dict[str, Any]:
        """分析测试结果"""
        if not results:
            return {'test_name': test_name, 'error': 'No results'}
        
        response_times = [r['response_time'] for r in results if r['success']]
        success_count = sum(1 for r in results if r['success'])
        error_count = len(results) - success_count
        
        if not response_times:
            return {
                'test_name': test_name,
                'total_requests': len(results),
                'success_count': success_count,
                'error_count': error_count,
                'success_rate': 0,
                'error': 'No successful requests'
            }
        
        return {
            'test_name': test_name,
            'total_requests': len(results),
            'success_count': success_count,
            'error_count': error_count,
            'success_rate': success_count / len(results) * 100,
            'response_times': {
                'min': min(response_times),
                'max': max(response_times),
                'avg': statistics.mean(response_times),
                'median': statistics.median(response_times),
                'p95': self._percentile(response_times, 95),
                'p99': self._percentile(response_times, 99)
            }
        }
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """计算百分位数"""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def print_results(self, results: Dict[str, Any]):
        """打印测试结果"""
        print(f"\n=== {results['test_name']} 测试结果 ===")
        print(f"总请求数: {results['total_requests']}")
        print(f"成功请求: {results['success_count']}")
        print(f"失败请求: {results['error_count']}")
        print(f"成功率: {results['success_rate']:.2f}%")
        
        if 'response_times' in results:
            rt = results['response_times']
            print(f"响应时间:")
            print(f"  最小: {rt['min']:.3f}s")
            print(f"  最大: {rt['max']:.3f}s")
            print(f"  平均: {rt['avg']:.3f}s")
            print(f"  中位数: {rt['median']:.3f}s")
            print(f"  P95: {rt['p95']:.3f}s")
            print(f"  P99: {rt['p99']:.3f}s")
        
        if 'requests_per_second' in results:
            print(f"吞吐量: {results['requests_per_second']:.2f} 请求/秒")
        
        if 'error' in results:
            print(f"错误: {results['error']}")

async def main():
    """主测试函数"""
    print("开始性能测试...")
    
    async with PerformanceTester() as tester:
        # 登录
        if not await tester.login():
            print("登录失败，退出测试")
            return
        
        print("登录成功，开始测试...")
        
        # 基础性能测试
        dashboard_results = await tester.test_dashboard_stats(20)
        tester.print_results(dashboard_results)
        
        student_results = await tester.test_student_list(20)
        tester.print_results(student_results)
        
        records_results = await tester.test_test_records(20)
        tester.print_results(records_results)
        
        # 并发压力测试
        print("\n开始并发压力测试...")
        concurrent_results = await tester.test_concurrent_requests(
            '/api/dashboard/stats', 
            concurrent_users=50, 
            requests_per_user=5
        )
        tester.print_results(concurrent_results)
        
        # 性能评估
        print("\n=== 性能评估 ===")
        if dashboard_results.get('response_times', {}).get('p95', 0) < 0.5:
            print("✅ 仪表板统计接口性能良好 (P95 < 500ms)")
        else:
            print("❌ 仪表板统计接口性能需要优化 (P95 >= 500ms)")
        
        if concurrent_results.get('success_rate', 0) >= 95:
            print("✅ 并发性能良好 (成功率 >= 95%)")
        else:
            print("❌ 并发性能需要优化 (成功率 < 95%)")
        
        if concurrent_results.get('requests_per_second', 0) >= 100:
            print("✅ 吞吐量良好 (>= 100 RPS)")
        else:
            print("❌ 吞吐量需要优化 (< 100 RPS)")

if __name__ == "__main__":
    asyncio.run(main())
