# psy_admin_fastapi/crud.py

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import HTTPException

from psy_admin_fastapi import models, schemas
from psy_admin_fastapi.security import get_password_hash, verify_password
import pandas as pd
import os

from psy_admin_fastapi.utils.cache import cached_query


###
###


# --- 管理员用户 CRUD ---

def get_admin_user(db: Session, user_id: int):
    return db.query(models.AdminUser).filter(models.AdminUser.id == user_id).first()


def get_admin_user_by_username(db: Session, username: str):
    return db.query(models.AdminUser).filter(models.AdminUser.username == username).first()


def get_admin_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.AdminUser).offset(skip).limit(limit).all()


def create_admin_user(db: Session, user: schemas.AdminUserCreate):
    db_user = get_admin_user_by_username(db, user.username)
    if db_user:
        raise ValueError("Username already registered")

    hashed_password = get_password_hash(user.password)
    db_user = models.AdminUser(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_admin_user(db: Session, username: str, password: str):
    user = get_admin_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def get_student(db: Session, student_id: str):
    """根据学号获取单个学生"""
    return db.query(models.Student).filter(models.Student.student_id == student_id).first()


def validate_student_id(db: Session, student_id: str):
    """根据学号校验学生是否存在"""
    return db.query(models.Student).filter(models.Student.student_id == student_id).first()


def create_student(db: Session, student: schemas.StudentCreate):
    """创建单个学生"""
    db_student = models.Student(**student.dict())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


def batch_create_students(db: Session, students: List[schemas.ExcelImportSchema]):
    """批量创建学生"""
    # 为每个学生添加 created_at 字段
    db_students = []
    for student in students:
        student_data = student.dict()
        student_data['created_at'] = datetime.utcnow()  # 添加创建时间
        db_students.append(models.Student(**student_data))

    db.bulk_save_objects(db_students)
    db.commit()
    return db_students


def update_student(db: Session, student_id: str, student_update: schemas.StudentUpdate):
    """更新学生信息"""
    db_student = get_student(db, student_id)
    if not db_student:
        return None

    # 仅更新传入的字段
    update_data = student_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_student, key, value)

    db.commit()
    db.refresh(db_student)
    return db_student


def delete_student(db: Session, student_id: str):
    """删除学生及其相关数据"""
    db_student = get_student(db, student_id)
    if not db_student:
        return False
    
    # 先删除相关的检测记录
    from psy_admin_fastapi.models import Test, Score, PhysiologicalData
    
    # 获取该学生的所有检测记录
    tests = db.query(Test).filter(Test.student_fk_id == db_student.id).all()
    
    for test in tests:
        # 删除检测记录相关的得分数据
        db.query(Score).filter(Score.test_fk_id == test.id).delete()
        # 删除检测记录相关的生理数据
        db.query(PhysiologicalData).filter(PhysiologicalData.test_fk_id == test.id).delete()
        # 删除检测记录
        db.delete(test)
    
    # 最后删除学生记录
    db.delete(db_student)
    db.commit()
    return True


def get_students_with_filters(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        class_name: Optional[str] = None,
        gender: Optional[str] = None,
        sort_by: str = "name",
        sort_order: str = "asc"
):
    """带筛选和排序的学生列表查询"""
    query = db.query(models.Student)

    # 筛选条件
    if class_name:
        query = query.filter(models.Student.class_name == class_name)
    if gender:
        query = query.filter(models.Student.gender == gender)

    # 排序处理
    sort_column = getattr(models.Student, sort_by, models.Student.name)
    if sort_order == "desc":
        sort_column = sort_column.desc()

    query = query.order_by(sort_column)
    return query.offset(skip).limit(limit).all()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    from jose import jwt
    from psy_admin_fastapi.config import settings
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


# --- 登录日志 CRUD ---
def log_login_attempt(db: Session, username: str, success: bool, message: Optional[str] = None):
    db_log = models.LoginLog(username=username, success=success, message=message)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


# --- 心理检测数据 CRUD (新增部分) ---

def create_test_data(db: Session, test_data: schemas.TestDataUpload):
    # 首先尝试通过学号查找学生
    student = db.query(models.Student).filter(models.Student.student_id == test_data.student_id).first()
    if not student:
        # 如果学生不存在，创建新的学生记录
        student = models.Student(
            student_id=test_data.student_id,
            name=test_data.name,
            gender=test_data.gender,
            class_name=getattr(test_data, 'class_name', None) or "未知班级"  # 使用提供的班级或默认值
        )
        db.add(student)
        db.flush()

    # 科学的异常判断逻辑
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

    # 综合判断异常状态
    is_abnormal = False
    abnormal_modules = []

    # 检查各模块得分
    if is_score_abnormal(test_data.questionnaire_scores.焦虑, "焦虑"):
        is_abnormal = True
        abnormal_modules.append("焦虑")
    if is_score_abnormal(test_data.questionnaire_scores.抑郁, "抑郁"):
        is_abnormal = True
        abnormal_modules.append("抑郁")
    if is_score_abnormal(test_data.questionnaire_scores.压力, "压力"):
        is_abnormal = True
        abnormal_modules.append("压力")

    # 如果有多个模块异常，在AI总结中特别标注
    if len(abnormal_modules) > 1:
        test_data.ai_summary = f"检测出多维度异常（{', '.join(abnormal_modules)}），建议重点关注和进一步评估。{test_data.ai_summary}"
    elif len(abnormal_modules) == 1:
        test_data.ai_summary = f"检测出{abnormal_modules[0]}风险，建议进一步评估。{test_data.ai_summary}"

    db_test = models.Test(
        student_fk_id=student.id,
        test_time=test_data.test_time,
        ai_summary=test_data.ai_summary,
        report_file_path=test_data.report_file_path,
        is_abnormal=is_abnormal,
        status="pending"  # 设置默认状态为待处理
    )
    db.add(db_test)
    db.flush()

    # ✅ 手动添加每个字段
    if test_data.questionnaire_scores.焦虑 is not None:
        db.add(models.Score(test_fk_id=db_test.id, module_name="焦虑", score=test_data.questionnaire_scores.焦虑))
    if test_data.questionnaire_scores.抑郁 is not None:
        db.add(models.Score(test_fk_id=db_test.id, module_name="抑郁", score=test_data.questionnaire_scores.抑郁))
    if test_data.questionnaire_scores.压力 is not None:
        db.add(models.Score(test_fk_id=db_test.id, module_name="压力", score=test_data.questionnaire_scores.压力))

    if test_data.physiological_data_summary.心率 is not None:
        db.add(models.PhysiologicalData(test_fk_id=db_test.id, data_key="心率",
                                        data_value=test_data.physiological_data_summary.心率))
    if test_data.physiological_data_summary.脑电alpha is not None:
        db.add(models.PhysiologicalData(test_fk_id=db_test.id, data_key="脑电alpha",
                                        data_value=test_data.physiological_data_summary.脑电alpha))

    db.commit()
    db.refresh(db_test)
    return db_test


@cached_query(ttl=120)  # 缓存2分钟
def get_test_records(
        db: Session,
        user_id: Optional[str] = None,
        user_name: Optional[str] = None,
        gender: Optional[str] = None,
        class_name: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        is_abnormal: Optional[bool] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
) -> List[models.Test]:
    """
    获取检测记录列表，使用 joinedload 预加载关联数据，避免 N+1 查询。
    """
    query = db.query(models.Test).join(models.Student) \
        .options(joinedload(models.Test.student)) \
        .options(joinedload(models.Test.scores)) \
        .options(joinedload(models.Test.physiological_data))

    if user_id:
        query = query.filter(models.Student.student_id == user_id)
    if user_name:
        query = query.filter(models.Student.name.contains(user_name))
    if gender:
        query = query.filter(models.Student.gender == gender)
    if class_name:
        query = query.filter(models.Student.class_name == class_name)
    if start_time:
        query = query.filter(models.Test.test_time >= start_time)
    if end_time:
        query = query.filter(models.Test.test_time <= end_time)
    if is_abnormal is not None:
        query = query.filter(models.Test.is_abnormal == is_abnormal)
    if status is not None:
        query = query.filter(models.Test.status == status)

    query = query.order_by(models.Test.test_time.desc())

    return query.offset(skip).limit(limit).all()


def get_test_record_detail(db: Session, record_id: int) -> Optional[models.Test]:
    """
    根据ID获取单个检测记录的详情，使用 joinedload 预加载关联数据。
    """
    record = db.query(models.Test) \
        .options(joinedload(models.Test.student)) \
        .options(joinedload(models.Test.scores)) \
        .options(joinedload(models.Test.physiological_data)) \
        .filter(models.Test.id == record_id).first()
    return record


def get_test_count(
        db: Session,
        user_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        is_abnormal: Optional[bool] = None
) -> int:
    query = db.query(func.count(models.Test.id)).join(models.Student)

    if user_id:
        query = query.filter(models.Student.student_id == user_id)
    if start_time:
        query = query.filter(models.Test.test_time >= start_time)
    if end_time:
        query = query.filter(models.Test.test_time <= end_time)
    if is_abnormal is not None:
        query = query.filter(models.Test.is_abnormal == is_abnormal)

    return query.scalar()


def get_tests_for_export(
        db: Session,
        user_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        is_abnormal: Optional[bool] = None
) -> List[models.Test]:
    return get_test_records(db, user_id, start_time, end_time, is_abnormal, 0, 99999999)


def delete_test_record(db: Session, record_id: int):
    """
    删除指定ID的检测记录及其所有关联数据。
    """
    db_record = db.query(models.Test).filter(models.Test.id == record_id).first()
    if db_record:
        # 删除与该记录关联的 PhysiologicalData
        db.query(models.PhysiologicalData).filter(models.PhysiologicalData.test_fk_id == record_id).delete(
            synchronize_session=False)
        # 删除与该记录关联的 Score
        db.query(models.Score).filter(models.Score.test_fk_id == record_id).delete(synchronize_session=False)
        # 最后删除 Test 记录本身
        db.delete(db_record)
        db.commit()
    return True


# --- 状态管理相关 CRUD 函数 ---

def get_test_record_status(db: Session, record_id: int):
    """
    获取单个检测记录的状态
    """
    record = db.query(models.Test).filter(models.Test.id == record_id).first()
    if not record:
        return None
    return {
        "id": record.id,
        "test_time": record.test_time,
        "is_abnormal": record.is_abnormal,
        "status": record.status,
        "ai_summary": record.ai_summary
    }


def update_test_record_status(db: Session, record_id: int, status_update: schemas.TestRecordStatusUpdate):
    """
    更新检测记录状态
    """
    record = db.query(models.Test).filter(models.Test.id == record_id).first()
    if not record:
        return None

    # 更新状态
    record.status = status_update.status
    if status_update.ai_summary:
        record.ai_summary = status_update.ai_summary

    db.commit()
    db.refresh(record)
    return record


def get_test_records_batch_status(db: Session, student_ids: Optional[List[str]] = None):
    """
    批量获取检测记录状态
    """
    query = db.query(models.Test).join(models.Student)

    if student_ids:
        query = query.filter(models.Student.student_id.in_(student_ids))

    records = query.all()

    # 统计状态
    status_counts = {
        "total_count": len(records),
        "abnormal_count": sum(1 for r in records if r.is_abnormal),
        "pending_count": sum(1 for r in records if r.status == "pending"),
        "processing_count": sum(1 for r in records if r.status == "processing"),
        "completed_count": sum(1 for r in records if r.status == "completed"),
        "failed_count": sum(1 for r in records if r.status == "failed")
    }

    # 转换为响应格式
    record_statuses = []
    for record in records:
        record_statuses.append({
            "id": record.id,
            "test_time": record.test_time,
            "is_abnormal": record.is_abnormal,
            "status": record.status,
            "ai_summary": record.ai_summary
        })

    return {
        "records": record_statuses,
        **status_counts
    }


def get_student_test_records_status(db: Session, student_id: str):
    """
    获取指定学生的检测记录状态
    """
    records = db.query(models.Test).join(models.Student).filter(
        models.Student.student_id == student_id
    ).all()

    if not records:
        raise HTTPException(status_code=404, detail="学生未找到或没有检测记录")

    # 统计状态
    status_counts = {
        "total_count": len(records),
        "abnormal_count": sum(1 for r in records if r.is_abnormal),
        "pending_count": sum(1 for r in records if r.status == "pending"),
        "processing_count": sum(1 for r in records if r.status == "processing"),
        "completed_count": sum(1 for r in records if r.status == "completed"),
        "failed_count": sum(1 for r in records if r.status == "failed")
    }

    # 转换为响应格式
    record_statuses = []
    for record in records:
        record_statuses.append({
            "id": record.id,
            "test_time": record.test_time,
            "is_abnormal": record.is_abnormal,
            "status": record.status,
            "ai_summary": record.ai_summary
        })

    return {
        "records": record_statuses,
        **status_counts
    }


# === 客户端对接相关 CRUD 函数 ===

def validate_student_for_client(db: Session, student_id: str):
    """
    客户端学号验证，返回学生基本信息
    """
    try:
        student = db.query(models.Student).filter(models.Student.student_id == student_id).first()
        if not student:
            return {"exists": False, "student_info": None}

        return {
            "exists": True,
            "student_info": {
                "student_id": student.student_id,
                "name": student.name,
                "class_name": student.class_name,
                "gender": student.gender
            }
        }
    except Exception as e:
        # 记录错误并重新抛出
        import logging
        logging.error(f"学号验证失败: {e}")
        raise


def create_client_test_data(db: Session, test_data: schemas.ClientTestDataUpload, pdf_file_path: str = None):
    """
    创建客户端上传的检测数据
    """
    # 首先尝试通过学号查找学生
    student = db.query(models.Student).filter(models.Student.student_id == test_data.student_id).first()
    if not student:
        # 如果学生不存在，创建新的学生记录
        student = models.Student(
            student_id=test_data.student_id,
            name=test_data.name,
            gender=test_data.gender,
            class_name=getattr(test_data, 'class_name', None) or "未知班级"  # 使用提供的班级或默认值
        )
        db.add(student)
        db.flush()

    # 科学的异常判断逻辑
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

    # 综合判断异常状态
    is_abnormal = False
    abnormal_modules = []

    # 检查各模块得分
    if is_score_abnormal(test_data.questionnaire_scores.焦虑, "焦虑"):
        is_abnormal = True
        abnormal_modules.append("焦虑")
    if is_score_abnormal(test_data.questionnaire_scores.抑郁, "抑郁"):
        is_abnormal = True
        abnormal_modules.append("抑郁")
    if is_score_abnormal(test_data.questionnaire_scores.压力, "压力"):
        is_abnormal = True
        abnormal_modules.append("压力")

    # 如果有多个模块异常，在AI总结中特别标注
    if len(abnormal_modules) > 1:
        test_data.ai_summary = f"检测出多维度异常（{', '.join(abnormal_modules)}），建议重点关注和进一步评估。{test_data.ai_summary}"
    elif len(abnormal_modules) == 1:
        test_data.ai_summary = f"检测出{abnormal_modules[0]}风险，建议进一步评估。{test_data.ai_summary}"

    # 创建检测记录
    db_test = models.Test(
        student_fk_id=student.id,
        test_time=test_data.test_time,
        ai_summary=test_data.ai_summary,
        report_file_path=pdf_file_path or test_data.report_file_path,
        is_abnormal=is_abnormal,
        status="completed"  # 客户端上传的数据默认为已完成状态
    )
    db.add(db_test)
    db.flush()

    # 添加问卷得分
    if test_data.questionnaire_scores.焦虑 is not None:
        db.add(models.Score(test_fk_id=db_test.id, module_name="焦虑", score=test_data.questionnaire_scores.焦虑))
    if test_data.questionnaire_scores.抑郁 is not None:
        db.add(models.Score(test_fk_id=db_test.id, module_name="抑郁", score=test_data.questionnaire_scores.抑郁))
    if test_data.questionnaire_scores.压力 is not None:
        db.add(models.Score(test_fk_id=db_test.id, module_name="压力", score=test_data.questionnaire_scores.压力))

    # 添加生理数据
    if test_data.physiological_data_summary.心率 is not None:
        db.add(models.PhysiologicalData(test_fk_id=db_test.id, data_key="心率",
                                        data_value=test_data.physiological_data_summary.心率))
    if test_data.physiological_data_summary.脑电alpha is not None:
        db.add(models.PhysiologicalData(test_fk_id=db_test.id, data_key="脑电alpha",
                                        data_value=test_data.physiological_data_summary.脑电alpha))

    db.commit()
    db.refresh(db_test)
    return db_test


def get_student_test_status_for_client(db: Session, student_id: str):
    """
    获取学生检测状态（客户端专用）
    """
    # 检查学生是否存在
    student = db.query(models.Student).filter(models.Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")

    # 查询该学生的检测记录
    records = db.query(models.Test).join(models.Student).filter(
        models.Student.student_id == student_id
    ).order_by(models.Test.test_time.desc()).all()

    if not records:
        return {
            "student_id": student_id,
            "status": "not_started",
            "is_abnormal": None,
            "latest_test_time": None,
            "test_record_count": 0
        }

    # 获取最新的检测记录
    latest_record = records[0]

    # 判断状态
    if latest_record.status == "completed":
        status = "completed"
    elif latest_record.status in ["pending", "processing"]:
        status = "in_progress"
    else:
        status = "not_started"

    return {
        "student_id": student_id,
        "status": status,
        "is_abnormal": latest_record.is_abnormal,
        "latest_test_time": latest_record.test_time,
        "test_record_count": len(records)
    }


# --- 数据导出相关函数 ---

def export_students_to_excel(db: Session, skip: int = 0, limit: int = 10000) -> str:
    """导出学生数据到Excel文件"""
    students = get_students_with_filters(db, skip=0, limit=limit)

    if not students:
        raise ValueError("没有可导出的学生数据")

    # 准备数据
    data = []
    for student in students:
        data.append({
            "学号": student.student_id,
            "姓名": student.name,
            "班级": student.class_name,
            "性别": student.gender,
            "创建时间": student.created_at.strftime("%Y-%m-%d %H:%M:%S") if student.created_at else ""
        })

    # 创建DataFrame并导出
    df = pd.DataFrame(data)

    # 导出目录
    export_dir = "exports"
    os.makedirs(export_dir, exist_ok=True)

    # 生成文件名
    filename = f"学生数据_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    filepath = os.path.join(export_dir, filename)

    # 保存Excel文件
    df.to_excel(filepath, index=False, engine="openpyxl")

    return filepath


def export_test_records_to_excel(db: Session, user_id: Optional[str] = None,
                                 start_time: Optional[datetime] = None,
                                 end_time: Optional[datetime] = None,
                                 is_abnormal: Optional[bool] = None,
                                 status: Optional[str] = None) -> str:
    """导出检测记录数据到Excel文件"""

    # 获取所有符合条件的记录
    records = get_test_records(db, user_id=user_id, start_time=start_time,
                               end_time=end_time, is_abnormal=is_abnormal,
                               status=status, skip=0, limit=999999)

    if not records:
        raise ValueError("没有可导出的检测记录数据")

    # 准备数据
    data = []
    for record in records:
        # 获取问卷得分
        scores_dict = {}
        for score in record.scores:
            scores_dict[score.module_name] = score.score

        # 获取生理数据
        phys_data_dict = {}
        for phys_data in record.physiological_data:
            phys_data_dict[phys_data.data_key] = phys_data.data_value

        data.append({
            "记录ID": record.id,
            "学号": record.student.student_id,
            "姓名": record.student.name,
            "班级": record.student.class_name,
            "性别": record.student.gender,
            "检测时间": record.test_time.strftime("%Y-%m-%d %H:%M:%S") if record.test_time else "",
            "AI评估总结": record.ai_summary or "",
            "是否异常": "是" if record.is_abnormal else "否",
            "状态": record.status,
            "报告文件路径": record.report_file_path or "",
            **scores_dict,  # 展开问卷得分
            **phys_data_dict  # 展开生理数据
        })

    # 创建DataFrame并导出
    df = pd.DataFrame(data)

    # 导出目录
    export_dir = "exports"
    os.makedirs(export_dir, exist_ok=True)

    # 生成文件名
    filename = f"检测记录数据_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    filepath = os.path.join(export_dir, filename)

    # 保存Excel文件
    df.to_excel(filepath, index=False, engine="openpyxl")

    return filepath


def export_dashboard_stats_to_excel(db: Session) -> str:
    """导出仪表板统计数据到Excel文件"""

    # 获取统计数据
    total_students = len(get_students_with_filters(db, skip=0, limit=999999))
    all_records = get_test_records(db, skip=0, limit=999999)
    total_records = len(all_records)
    abnormal_records = [r for r in all_records if r.is_abnormal]
    abnormal_count = len(abnormal_records)

    # 获取今日记录数
    today = datetime.now().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_records = get_test_records(db, start_time=today_start, skip=0, limit=999999)
    today_count = len(today_records)

    # 获取班级分布
    students = get_students_with_filters(db, skip=0, limit=999999)
    class_distribution = {}
    for student in students:
        class_name = student.class_name
        class_distribution[class_name] = class_distribution.get(class_name, 0) + 1

    # 获取得分统计
    score_stats = {
        "焦虑": [],
        "抑郁": [],
        "压力": []
    }

    for record in all_records:
        for score in record.scores:
            if score.module_name in score_stats:
                score_stats[score.module_name].append(score.score)

    # 计算每个分数段的分布
    score_distribution = {}
    for module_name, scores in score_stats.items():
        distribution = {
            "0-10": 0,
            "11-15": 0,
            "16-20": 0,
            "21-25": 0,
            "26-30": 0
        }

        for score in scores:
            if score <= 10:
                distribution["0-10"] += 1
            elif score <= 15:
                distribution["11-15"] += 1
            elif score <= 20:
                distribution["16-20"] += 1
            elif score <= 25:
                distribution["21-25"] += 1
            else:
                distribution["26-30"] += 1

        score_distribution[module_name] = distribution

    # 创建多sheet的Excel文件
    export_dir = "exports"
    os.makedirs(export_dir, exist_ok=True)

    filename = f"仪表板统计数据_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    filepath = os.path.join(export_dir, filename)

    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        # 统计概览sheet
        stats_data = {
            "指标": ["总学生数", "总检测记录数", "异常记录数", "今日检测数"],
            "数值": [total_students, total_records, abnormal_count, today_count]
        }
        pd.DataFrame(stats_data).to_excel(writer, sheet_name='统计概览', index=False)

        # 班级分布sheet
        class_data = []
        for class_name, count in class_distribution.items():
            class_data.append({"班级": class_name, "学生数": count})
        pd.DataFrame(class_data).to_excel(writer, sheet_name='班级分布', index=False)

        # 得分分布sheet
        score_data = []
        for module_name, distribution in score_distribution.items():
            for score_range, count in distribution.items():
                score_data.append({
                    "模块": module_name,
                    "分数段": score_range,
                    "人数": count
                })
        pd.DataFrame(score_data).to_excel(writer, sheet_name='得分分布', index=False)

    return filepath


# 新增函数：获取所有学号（用于批量导入去重）
def get_all_student_ids(db: Session):
    """获取所有学生的学号，用于批量导入时的去重检查"""
    result = db.query(models.Student.student_id).all()
    return [row[0] for row in result]


# 新增函数：聚合查询仪表板统计
def get_dashboard_stats_aggregated(db: Session):
    """使用聚合查询获取仪表板统计数据"""
    from sqlalchemy import func, and_
    from datetime import datetime, date

    # 学生总数
    total_students = db.query(func.count(models.Student.id)).scalar()

    # 检测记录总数
    total_records = db.query(func.count(models.Test.id)).scalar()

    # 异常记录数
    abnormal_count = db.query(func.count(models.Test.id)).filter(
        models.Test.is_abnormal == True
    ).scalar()

    # 今日记录数
    today = date.today()
    today_start = datetime.combine(today, datetime.min.time())
    today_count = db.query(func.count(models.Test.id)).filter(
        models.Test.test_time >= today_start
    ).scalar()

    return {
        "total_students": total_students or 0,
        "total_records": total_records or 0,
        "abnormal_count": abnormal_count or 0,
        "today_records": today_count or 0
    }