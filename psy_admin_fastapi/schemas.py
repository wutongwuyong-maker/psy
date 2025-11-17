# psy_admin_fastapi/schemas.py

from pydantic import BaseModel, EmailStr,Field  # 确保导入 EmailStr (如果 AdminUser 有邮箱)
from datetime import datetime
from typing import Dict, Optional, List


# --- 输入模型 (用于接收请求体) ---

class AdminUserCreate(BaseModel):
    username: str
    password: str
    email: Optional[EmailStr] = None  # 假设管理员用户可能包含邮箱
    is_active: bool = True  # 默认激活状态


# 检测系统上传数据模型
class QuestionnaireScoreItem(BaseModel):
    """单个问卷模块的得分项"""
    score: int
    max_score: int
    level: str  # 重度、中度、轻度
    feedback: Optional[str] = None


class QuestionnaireScoresBase(BaseModel):
    """问卷得分结构"""
    学习焦虑: Optional[QuestionnaireScoreItem] = None
    对人焦虑: Optional[QuestionnaireScoreItem] = None
    孤独倾向: Optional[QuestionnaireScoreItem] = None
    自责倾向: Optional[QuestionnaireScoreItem] = None


class PhysiologicalDataBase(BaseModel):
    心率: Optional[float] = None
    脑电alpha: Optional[float] = None


class TestDataUpload(BaseModel):
    student_id: str
    name: str
    gender: str
    age: int
    test_time: datetime
    questionnaire_scores: QuestionnaireScoresBase
    physiological_data_summary: PhysiologicalDataBase
    ai_summary: str
    report_file_path: str

    class Config:
        from_attributes = True  # Pydantic v2 使用 from_attributes=True 代替 orm_mode=True


# --- 输出模型 (用于返回给前端的数据结构) ---

# 新增：AdminUser 模型，用于 FastAPI 响应 AdminUser 对象
class AdminUser(BaseModel):
    id: int
    username: str
    email: Optional[EmailStr] = None  # 根据 models.py 中的 AdminUser 定义
    is_active: bool = True

    # 如果 models.py 中的 AdminUser 还有其他需要返回的字段，请在这里添加，但不要包含密码！

    class Config:
        from_attributes = True




class User(BaseModel):
    id: int
    user_id: str
    name: str
    gender: Optional[str] = None
    age: Optional[int] = None

    class Config:
        from_attributes = True


class ScoreBase(BaseModel):
    id: int
    module_name: str
    score: int
    max_score: Optional[int] = None
    level: Optional[str] = None
    questionnaire_feedback: Optional[str] = None

    class Config:
        from_attributes = True


class PhysiologicalDataOut(BaseModel):
    id: int
    data_key: str
    data_value: float

    class Config:
        from_attributes = True


class TestBase(BaseModel):
    id: int
    test_time: datetime
    ai_summary: Optional[str] = None
    report_file_path: Optional[str] = None
    is_abnormal: bool

    class Config:
        from_attributes = True


# 完整检测详情输出模型
class TestDetail(TestBase):
    user: User  # 包含用户基本信息
    scores: List[ScoreBase] = []  # 包含问卷得分列表
    physiological_data: List[PhysiologicalDataOut] = []  # 包含生理数据列表

    class Config:
        from_attributes = True


# JWT 相关的 Schema (保持不变，只是位置调整到 AdminUser 之后，逻辑上更清晰)
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None
# --- 新增：用于表示问卷得分和生理数据的详细结构 ---
class ScoreDetail(BaseModel):
    module_name: str
    score: int
    max_score: Optional[int] = None
    level: Optional[str] = None
    questionnaire_feedback: Optional[str] = None

    class Config:
        from_attributes = True # 以前是 orm_mode = True

class PhysiologicalDataDetail(BaseModel):
    data_key: str
    data_value: float

    class Config:
        from_attributes = True # 以前是 orm_mode = True

# --- 新增：用于表示学生的详细结构 ---
class StudentDetail(BaseModel):
    id: int
    student_id: str
    name: str
    class_name: str
    gender: str
    created_at: datetime

    class Config:
        from_attributes = True # 以前是 orm_mode = True


# --- 新增：用于表示单个测试记录及其所有关联数据的详细结构 ---
class TestRecordDetail(BaseModel):
    id: int
    student_fk_id: int # 外键，表示关联的学生ID
    test_time: datetime
    ai_summary: Optional[str] = None
    report_file_path: Optional[str] = None
    is_abnormal: bool = False
    status: str = "pending"

    # 关联数据：
    student: StudentDetail # 关联的学生信息
    scores: List[ScoreDetail] = [] # 关联的问卷得分列表
    physiological_data: List[PhysiologicalDataDetail] = [] # 关联的生理数据列表

    class Config:
        from_attributes = True # 以前是 orm_mode = True

class StudentBase(BaseModel):
    name: str
    student_id: str
    class_name: str
    gender: str

class StudentCreate(StudentBase):
    pass

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    student_id: Optional[str] = None
    class_name: Optional[str] = None
    gender: Optional[str] = None

class ExcelImportSchema(StudentBase):
    class Config:
        from_attributes = True

class Student(StudentBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

class StudentIDRequest(BaseModel):
    student_id: str

class BatchDeleteStudentsRequest(BaseModel):
    """批量删除学生请求"""
    student_ids: List[str]

# --- 状态管理相关 schemas ---
class StudentBatchQuery(BaseModel):
    """批量学生查询请求"""
    student_ids: List[str]

class TestRecordStatus(BaseModel):
    """检测记录状态"""
    id: int
    test_time: datetime
    is_abnormal: bool
    status: str  # 状态：pending, processing, completed, failed
    ai_summary: Optional[str] = None

class TestRecordStatusUpdate(BaseModel):
    """检测记录状态更新请求"""
    status: str  # 状态：pending, processing, completed, failed
    ai_summary: Optional[str] = None

class BatchGenerateReportsRequest(BaseModel):
    """批量生成报告请求"""
    record_ids: List[int]
    format: str = "pdf"  # pdf 或 excel

class BatchDeleteTestRecordsRequest(BaseModel):
    """批量删除检测记录请求"""
    record_ids: List[int]

class TestRecordBatchStatus(BaseModel):
    """批量状态查询响应"""
    records: List[TestRecordStatus]
    total_count: int
    abnormal_count: int
    pending_count: int
    processing_count: int
    completed_count: int
    failed_count: int

# === 客户端对接相关 schemas ===

class StudentValidateRequest(BaseModel):
    """客户端学号验证请求"""
    student_id: str

class StudentValidateResponse(BaseModel):
    """客户端学号验证响应"""
    exists: bool
    student_info: Optional[dict] = None

class ClientQuestionnaireScores(BaseModel):
    """客户端问卷得分"""
    学习焦虑: Optional[QuestionnaireScoreItem] = None
    对人焦虑: Optional[QuestionnaireScoreItem] = None
    孤独倾向: Optional[QuestionnaireScoreItem] = None
    自责倾向: Optional[QuestionnaireScoreItem] = None

class ClientPhysiologicalData(BaseModel):
    """客户端生理数据"""
    心率: Optional[float] = None
    脑电alpha: Optional[float] = None

class ClientTestDataUpload(BaseModel):
    """客户端检测数据上传"""
    student_id: str
    name: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    class_name: Optional[str] = None  # 添加班级字段
    test_time: datetime
    questionnaire_scores: ClientQuestionnaireScores
    physiological_data_summary: ClientPhysiologicalData
    ai_summary: Optional[str] = None
    report_file_path: str

class TestStatusResponse(BaseModel):
    """检测状态查询响应"""
    student_id: str
    status: str  # not_started, in_progress, completed
    is_abnormal: Optional[bool] = None
    latest_test_time: Optional[datetime] = None
    test_record_count: int = 0
