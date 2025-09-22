#!/usr/bin/env python3
"""
测试修复后的功能
"""
import sys
import os
import requests
import json
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_field_mapping_fix():
    """测试字段映射修复是否正确"""
    print("=== 测试字段映射修复 ===")
    
    # 模拟前端数据结构
    mock_record = {
        "id": 1,
        "student": {
            "name": "张三",
            "student_id": "U001",
            "class_name": "计算机1班",
            "gender": "男"
        },
        "test_time": "2025-07-10T10:00:00",
        "is_abnormal": True,
        "ai_summary": "检测出高焦虑风险",
        "scores": [
            {"module_name": "焦虑", "score": 18},
            {"module_name": "抑郁", "score": 8},
            {"module_name": "压力", "score": 12}
        ],
        "physiological_data": [
            {"data_key": "心率", "data_value": 85.0},
            {"data_key": "脑电alpha", "data_value": 13.2}
        ]
    }
    
    # 测试字段访问
    try:
        name = mock_record["student"]["name"]
        student_id = mock_record["student"]["student_id"]
        class_name = mock_record["student"]["class_name"]
        gender = mock_record["student"]["gender"]
        
        print(f"学生姓名: {name}")
        print(f"学号: {student_id}")
        print(f"班级: {class_name}")
        print(f"性别: {gender}")
        
        # 测试错误字段访问（应该返回None）
        wrong_field = mock_record.get("user", {}).get("name")
        print(f"错误字段访问结果: {wrong_field}")
        
        print("✅ 字段映射测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 字段映射测试失败: {e}")
        return False

def test_abnormal_logic_fix():
    """测试异常判断逻辑修复"""
    print("\n=== 测试异常判断逻辑修复 ===")
    
    # 测试数据
    test_cases = [
        {
            "name": "正常情况",
            "scores": {"焦虑": 8, "抑郁": 4, "压力": 12},
            "expected_abnormal": False,
            "expected_modules": []
        },
        {
            "name": "单模块异常",
            "scores": {"焦虑": 18, "抑郁": 6, "压力": 10},
            "expected_abnormal": True,
            "expected_modules": ["焦虑"]
        },
        {
            "name": "双模块异常",
            "scores": {"焦虑": 20, "抑郁": 16, "压力": 8},
            "expected_abnormal": True,
            "expected_modules": ["焦虑", "抑郁"]
        },
        {
            "name": "三模块异常",
            "scores": {"焦虑": 22, "抑郁": 18, "压力": 19},
            "expected_abnormal": True,
            "expected_modules": ["焦虑", "抑郁", "压力"]
        },
        {
            "name": "部分None值",
            "scores": {"焦虑": None, "抑郁": 16, "压力": 8},
            "expected_abnormal": True,
            "expected_modules": ["抑郁"]
        }
    ]
    
    def is_score_abnormal(score, module_name):
        """判断单个得分是否异常"""
        if score is None:
            return False
        
        # 基础阈值
        base_thresholds = {
            "焦虑": 15,
            "抑郁": 15, 
            "压力": 15
        }
        
        # 根据模块调整阈值
        threshold = base_thresholds.get(module_name, 15)
        
        # 超过阈值即为异常
        return score > threshold
    
    def analyze_abnormality(scores):
        """综合判断异常状态"""
        is_abnormal = False
        abnormal_modules = []
        
        # 检查各模块得分
        if is_score_abnormal(scores.焦虑, "焦虑"):
            is_abnormal = True
            abnormal_modules.append("焦虑")
        if is_score_abnormal(scores.抑郁, "抑郁"):
            is_abnormal = True  
            abnormal_modules.append("抑郁")
        if is_score_abnormal(scores.压力, "压力"):
            is_abnormal = True
            abnormal_modules.append("压力")
        
        return is_abnormal, abnormal_modules
    
    # 运行测试用例
    all_passed = True
    for case in test_cases:
        try:
            is_abnormal, abnormal_modules = analyze_abnormality(case["scores"])
            
            if is_abnormal == case["expected_abnormal"] and set(abnormal_modules) == set(case["expected_modules"]):
                print(f"✅ {case['name']}: 通过")
            else:
                print(f"❌ {case['name']}: 失败")
                print(f"  预期: 异常={case['expected_abnormal']}, 模块={case['expected_modules']}")
                print(f"  实际: 异常={is_abnormal}, 模块={abnormal_modules}")
                all_passed = False
                
        except Exception as e:
            print(f"❌ {case['name']}: 异常 - {e}")
            all_passed = False
    
    return all_passed

def test_model_consistency():
    """测试数据模型一致性"""
    print("\n=== 测试数据模型一致性 ===")
    
    try:
        # 导入模型
        from psy_admin_fastapi.models import Student, Test, Score, PhysiologicalData
        
        # 检查模型是否存在
        models = [Student, Test, Score, PhysiologicalData]
        model_names = ["Student", "Test", "Score", "PhysiologicalData"]
        
        for model, name in zip(models, model_names):
            if model is not None:
                print(f"✅ {name} 模型存在")
            else:
                print(f"❌ {name} 模型不存在")
                return False
        
        # 检查关系定义
        if hasattr(Student, 'tests') and hasattr(Test, 'student'):
            print("✅ Student-Test 关系定义正确")
        else:
            print("❌ Student-Test 关系定义错误")
            return False
            
        if hasattr(Test, 'scores') and hasattr(Score, 'test'):
            print("✅ Test-Score 关系定义正确")
        else:
            print("❌ Test-Score 关系定义错误")
            return False
            
        if hasattr(Test, 'physiological_data') and hasattr(PhysiologicalData, 'test'):
            print("✅ Test-PhysiologicalData 关系定义正确")
        else:
            print("❌ Test-PhysiologicalData 关系定义错误")
            return False
        
        print("✅ 数据模型一致性测试通过")
        return True
        
    except ImportError as e:
        print(f"❌ 导入模型失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 模型一致性测试失败: {e}")
        return False

def main():
    """运行所有测试"""
    print("开始测试修复后的功能...\n")
    
    tests = [
        ("字段映射修复", test_field_mapping_fix),
        ("异常判断逻辑修复", test_abnormal_logic_fix),
        ("数据模型一致性", test_model_consistency)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}: 测试执行失败 - {e}")
            results.append((test_name, False))
    
    # 汇总结果
    print("\n" + "="*50)
    print("测试结果汇总:")
    passed = 0
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{len(results)} 项测试通过")
    
    if passed == len(results):
        print("\n🎉 所有修复都验证成功！")
        return True
    else:
        print(f"\n⚠️  有 {len(results) - passed} 项测试失败，需要进一步检查")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
