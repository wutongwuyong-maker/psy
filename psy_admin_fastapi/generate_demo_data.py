#!/usr/bin/env python3
"""
演示数据生成脚本
生成1000个学生和2000条检测记录用于演示
"""

import sys
import os
import random
from datetime import datetime, timedelta
from typing import List

# 添加项目路径
sys.path.append(os.path.dirname(__file__))

from database import SessionLocal
from models import Student, Test, Score, PhysiologicalData
from crud import create_student, create_test_data
import schemas

def generate_student_data(count: int = 1000) -> List[schemas.StudentCreate]:
    """生成学生数据"""
    students = []
    
    # 班级列表
    classes = [
        "高一(1)班", "高一(2)班", "高一(3)班", "高一(4)班", "高一(5)班",
        "高二(1)班", "高二(2)班", "高二(3)班", "高二(4)班", "高二(5)班",
        "高三(1)班", "高三(2)班", "高三(3)班", "高三(4)班", "高三(5)班"
    ]
    
    # 姓名列表
    surnames = ["王", "李", "张", "刘", "陈", "杨", "赵", "黄", "周", "吴", 
                "徐", "孙", "胡", "朱", "高", "林", "何", "郭", "马", "罗"]
    given_names = ["伟", "芳", "娜", "秀英", "敏", "静", "丽", "强", "磊", "军",
                   "洋", "勇", "艳", "杰", "娟", "涛", "明", "超", "秀兰", "霞",
                   "平", "刚", "桂英", "建华", "文", "华", "金凤", "建国", "秀珍", "海燕"]
    
    for i in range(count):
        # 生成学号
        student_id = f"STU{str(i+1).zfill(6)}"
        
        # 生成姓名
        surname = random.choice(surnames)
        given_name = random.choice(given_names)
        name = surname + given_name
        
        # 生成班级
        class_name = random.choice(classes)
        
        # 生成性别
        gender = random.choice(["男", "女"])
        
        students.append(schemas.StudentCreate(
            name=name,
            student_id=student_id,
            class_name=class_name,
            gender=gender
        ))
    
    return students

def generate_test_data(student_ids: List[str], count: int = 2000) -> List[schemas.TestDataUpload]:
    """生成检测数据"""
    test_records = []
    
    for i in range(count):
        # 随机选择学生
        student_id = random.choice(student_ids)
        
        # 生成检测时间（过去30天内）
        days_ago = random.randint(0, 30)
        test_time = datetime.now() - timedelta(days=days_ago)
        
        # 生成问卷得分
        anxiety_score = random.randint(0, 30)  # 0-30分
        depression_score = random.randint(0, 30)  # 0-30分
        stress_score = random.randint(0, 30)  # 0-30分
        
        # 生成生理数据
        heart_rate = random.randint(60, 100)
        eeg_alpha = round(random.uniform(8.0, 13.0), 1)
        
        # 生成AI总结
        scores = [
            {"module_name": "焦虑", "score": anxiety_score},
            {"module_name": "抑郁", "score": depression_score},
            {"module_name": "压力", "score": stress_score}
        ]
        ai_summary = generate_ai_summary(scores)
        
        # 判断是否异常
        is_abnormal = any(score["score"] > 20 for score in scores)
        
        # 生成状态
        status = random.choice(["completed", "completed", "completed", "failed"])  # 大部分是完成状态
        
        # 创建符合TestDataUpload格式的数据
        test_record = schemas.TestDataUpload(
            student_id=student_id,
            name="",  # 这个字段在create_test_data函数中不会被使用，因为会从数据库中获取学生信息
            gender="",  # 同上
            age=0,  # 同上
            test_time=test_time,
            questionnaire_scores=schemas.QuestionnaireScoresBase(
                焦虑=anxiety_score,
                抑郁=depression_score,
                压力=stress_score
            ),
            physiological_data_summary=schemas.PhysiologicalDataBase(
                心率=heart_rate,
                脑电alpha=eeg_alpha
            ),
            ai_summary=ai_summary,
            report_file_path=""  # 空的文件路径
        )
        
        test_records.append(test_record)
    
    return test_records

def generate_ai_summary(scores: List[dict]) -> str:
    """生成AI总结"""
    summary_parts = []
    
    for score in scores:
        if score["score"] <= 10:
            level = "正常"
        elif score["score"] <= 20:
            level = "轻度"
        else:
            level = "中重度"
        
        summary_parts.append(f"{score['module_name']}水平{level}")
    
    return f"根据检测结果，该学生的{', '.join(summary_parts)}。建议关注心理健康状况，必要时寻求专业帮助。"

def main():
    """主函数"""
    print("开始生成演示数据...")
    
    db = SessionLocal()
    try:
        # 生成学生数据
        print("生成学生数据...")
        students_data = generate_student_data(1000)
        
        student_ids = []
        for i, student_data in enumerate(students_data):
            try:
                student = create_student(db, student_data)
                student_ids.append(student.student_id)
                if (i + 1) % 100 == 0:
                    print(f"  已创建 {i + 1} 个学生")
            except Exception as e:
                print(f"创建学生失败: {e}")
                continue
        
        print(f"成功创建 {len(student_ids)} 个学生")
        
        # 生成检测数据
        print("生成检测数据...")
        test_data = generate_test_data(student_ids, 2000)
        
        success_count = 0
        for i, test_record in enumerate(test_data):
            try:
                create_test_data(db, test_record)
                success_count += 1
                if (i + 1) % 200 == 0:
                    print(f"  已创建 {i + 1} 条检测记录")
            except Exception as e:
                print(f"创建检测记录失败: {e}")
                continue
        
        print(f"成功创建 {success_count} 条检测记录")
        
        # 统计信息
        total_students = db.query(Student).count()
        total_tests = db.query(Test).count()
        abnormal_tests = db.query(Test).filter(Test.is_abnormal == True).count()
        
        print("\n=== 数据统计 ===")
        print(f"总学生数: {total_students}")
        print(f"总检测记录数: {total_tests}")
        print(f"异常记录数: {abnormal_tests}")
        print(f"异常率: {abnormal_tests/total_tests*100:.1f}%")
        
        print("\n演示数据生成完成！")
        
    except Exception as e:
        print(f"生成演示数据失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
