from datetime import timedelta, datetime, timezone
import logging
from typing import Optional, List
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, Depends, HTTPException, status, Request, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError
from sqlalchemy.orm import Session
import pandas as pd
from typing import List
import crud, models, schemas
from database import engine, get_db_session, Base  # 导入数据库相关
from config import settings  # 导入你的配置
from dependencies import get_current_admin_user, oauth2_scheme  # 导入认证依赖和OAuth2 scheme
# 延迟导入报告服务，避免循环导入
# from services.report_service import generate_report_content, generate_pdf_report, generate_excel_report
from fastapi.responses import FileResponse
import os
from utils.concurrent import thread_pool, thread_safe_db
from utils.schema_migrations import ensure_core_schema

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 定义 lifespan 事件处理器
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时创建数据库表
    Base.metadata.create_all(bind=engine)
    logger.info("数据库表已检查/创建。")
    # 运行轻量级启动迁移，保证关键列与索引存在（后续可替换为 Alembic）
    try:
        ensure_core_schema()
        logger.info("启动迁移检查完成。")
    except Exception as e:
        logger.error(f"启动迁移检查失败: {e}")
    yield
    # 关闭时可以执行清理操作（如果有需要）
    logger.info("应用正在关闭...")

# 创建 FastAPI 应用实例，并传入 lifespan 事件处理器
app = FastAPI(
    title="心理检测管理系统API",
    description="提供心理检测管理系统的后端API服务，包括用户认证、题库管理、报告生成等功能。",
    version="1.0.0",
    lifespan=lifespan
)

# 配置 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# 认证接口：用于获取JWT令牌
@app.post("/token", response_model=schemas.Token, summary="获取JWT令牌")
async def login_for_access_token(
        request: Request,  # 引入 Request 获取客户端IP
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db_session)
):
    admin_user = crud.authenticate_admin_user(db, form_data.username, form_data.password)
    if not admin_user:
        # 用户不存在或密码不正确
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码不正确",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": admin_user.username}, expires_delta=access_token_expires
    )

    # 记录登录日志 (这里假设 LoginLog 模型和相关crud函数存在)
    try:
        login_ip = request.client.host if request.client else "unknown_ip"
        login_log = models.LoginLog(
            username=admin_user.username,
            login_time=datetime.utcnow(),
            login_ip=login_ip,
            status=1,  # 假设 1 代表成功
        )
        db.add(login_log)
        db.commit()
        db.refresh(login_log)
        logger.info("用户 '%s' 成功登录，IP: %s", admin_user.username, login_ip)
    except Exception as e:
        logger.error("记录登录日志失败: %s", e)
        # 即使记录日志失败，也不阻止用户登录
        pass

    return {"access_token": access_token, "token_type": "bearer"}

# JWT 相关的辅助函数 (生成访问令牌)
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """生成 JWT Token，包含过期时间"""
    # 校验关键配置
    if not settings.SECRET_KEY:
        raise ValueError("SECRET_KEY 未配置，无法生成 Token")
    algorithm = settings.ALGORITHM or "HS256"  # 设置默认算法

    to_encode = data.copy()
    # 计算过期时间（强制使用 UTC 时区）
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    try:
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=algorithm)
    except JWTError as e:
        # 可结合日志系统记录详细错误
        raise RuntimeError(f"JWT 生成失败: {e}") from e

    return encoded_jwt

# 示例受保护接口 1：获取当前认证用户的信息
@app.get("/users/me/", response_model=schemas.AdminUser, summary="获取当前管理员用户信息 (需要认证)")
async def read_users_me(
        current_user: models.AdminUser = Depends(get_current_admin_user)  # 依赖于认证
):
    return current_user

# 示例受保护接口 2：获取所有用户 (假设你的 crud.py 有 get_users 函数)
@app.get("/users/", response_model=list[schemas.User], summary="获取所有用户列表 (需要认证)")
async def read_all_users(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db_session),
        current_user: models.AdminUser = Depends(get_current_admin_user)  # 依赖于认证
):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

# 上传心理检测数据（使用线程池优化并发处理）
@app.post("/test-data/upload", response_model=schemas.TestRecordDetail, summary="上传心理检测数据")
async def upload_test_data(
    test_data: schemas.TestDataUpload,
    db: Session = Depends(get_db_session),
):
    try:
        # 使用线程池处理数据上传，提高并发性能
        future = thread_pool.submit(_process_upload_data, test_data)
        db_test_record = future.result(timeout=30)  # 设置30秒超时
        
        logger.info(f"成功接收并存储学生 {test_data.student_id} 的检测数据。")
        return db_test_record
    except Exception as e:
        logger.error(f"处理心理检测数据上传失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"数据上传失败: {e}"
        )

@thread_safe_db
def _process_upload_data(test_data: schemas.TestDataUpload, db: Session):
    """处理数据上传的线程安全函数"""
    try:
        db_test_record = crud.create_test_data(db, test_data)
        db.refresh(db_test_record)  # 确保最新状态
        db_test_record.student  # 访问以加载
        db_test_record.scores  # 访问以加载
        db_test_record.physiological_data  # 访问以加载
        return db_test_record
    except Exception as e:
        logger.error(f"线程池处理数据上传失败: {e}")
        raise

# 获取所有心理检测记录列表
@app.get("/test-data/records/", response_model=List[schemas.TestRecordDetail], summary="获取所有心理检测记录列表")
async def get_test_data_records(
    user_id: Optional[str] = None,
    user_name: Optional[str] = None,
    gender: Optional[str] = None,
    class_name: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    is_abnormal: Optional[bool] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db_session),
    current_user: models.AdminUser = Depends(get_current_admin_user)  # 需要认证
):
    records = crud.get_test_records(
        db, user_id, user_name, gender, class_name, start_time, end_time, is_abnormal, status, skip, limit
    )
    return records

# 获取单个心理检测记录详情
@app.get("/test-data/records/{record_id}", response_model=schemas.TestRecordDetail, summary="获取单个心理检测记录详情")
async def get_test_data_record_detail(
    record_id: int,
    db: Session = Depends(get_db_session),
    current_user: models.AdminUser = Depends(get_current_admin_user)  # 需要认证
):
    record = crud.get_test_record_detail(db, record_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="检测记录未找到")
    return record
@app.delete("/test-data/records/{record_id}", summary="删除检测记录")
async def delete_test_record(
    record_id: int,
    db: Session = Depends(get_db_session),
    current_user: models.AdminUser = Depends(get_current_admin_user),
):
    ok = crud.delete_test_record(db, record_id)
    if not ok:
        raise HTTPException(status_code=404, detail="记录不存在")
    return {"ok": True}

# 批量导入学生
@app.post("/api/students/batch-import")
async def batch_import_students(
    file: UploadFile = File(...),
    db: Session = Depends(get_db_session),
    current_user: models.AdminUser = Depends(get_current_admin_user)
):
    # 1. 读取Excel文件
    try:
        content = await file.read()
        from io import BytesIO
        df = pd.read_excel(BytesIO(content), engine="openpyxl")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Excel读取失败: {str(e)}")

    # 2. 验证列完整性
    required_cols = ["name", "student_id", "class_name", "gender"]
    missing_cols = set(required_cols) - set(df.columns)
    if missing_cols:
        raise HTTPException(status_code=400, detail=f"缺少必要列: {', '.join(missing_cols)}")

    # 3. 数据验证与去重
    valid_students = []
    duplicate_students = []
    error_rows = []
    
    # 批量查询现有学号
    existing_student_ids = set(crud.get_all_student_ids(db))
    
    for index, row in df.iterrows():
        try:
            # 数据验证
            if pd.isna(row["name"]) or pd.isna(row["student_id"]) or pd.isna(row["class_name"]) or pd.isna(row["gender"]):
                error_rows.append({
                    "row": index + 2,  # Excel行号（从2开始，因为第1行是标题）
                    "error": "必填字段不能为空"
                })
                continue
            
            student_id = str(row["student_id"]).strip()
            
            # 检查是否已存在
            if student_id in existing_student_ids:
                duplicate_students.append({
                    "row": index + 2,
                    "student_id": student_id,
                    "name": row["name"]
                })
                continue
            
            # 添加到有效列表
            valid_students.append(schemas.ExcelImportSchema(
                name=str(row["name"]).strip(),
                student_id=student_id,
                class_name=str(row["class_name"]).strip(),
                gender=str(row["gender"]).strip()
            ))
            existing_student_ids.add(student_id)  # 避免同一批次内重复
            
        except Exception as e:
            error_rows.append({
                "row": index + 2,
                "error": f"数据格式错误: {str(e)}"
            })

    # 4. 批量插入有效数据
    success_count = 0
    # test_record_count = 0  # 已移除：不再自动创建检测记录
    if valid_students:
        try:
            # 批量创建学生
            db_students = crud.batch_create_students(db, valid_students)
            success_count = len(valid_students)
            
            # 不再自动为每个新创建的学生创建待处理的检测记录
            # 检测记录应该在实际进行检测并上传数据时才创建
            # 之前的自动创建逻辑已完全移除
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"批量插入失败: {str(e)}")

    # 5. 返回详细结果
    return {
        "success_count": success_count,
        # "test_record_count": test_record_count,  # 已移除：不再返回检测记录数量
        "duplicate_count": len(duplicate_students),
        "error_count": len(error_rows),
        "duplicate_students": duplicate_students,
        "error_rows": error_rows,
        "detail": f"导入完成：成功 {success_count} 条学生，重复 {len(duplicate_students)} 条，错误 {len(error_rows)} 条"
    }

# 获取学生列表（支持筛选、排序、分页）
@app.get("/api/students", response_model=List[schemas.Student])
async def get_students(
    skip: int = 0,
    limit: int = 10000,  # 增加默认limit，支持获取更多数据
    class_name: Optional[str] = None,
    gender: Optional[str] = None,
    sort_by: str = "name",
    sort_order: str = "asc",
    db: Session = Depends(get_db_session),
    current_user: models.AdminUser = Depends(get_current_admin_user)
):
    # 限制最大limit，防止查询过大数据集
    if limit > 10000:
        limit = 10000
    
    students = crud.get_students_with_filters(
        db, skip=skip, limit=limit, class_name=class_name,
        gender=gender, sort_by=sort_by, sort_order=sort_order
    )
    
    logger.info(f"获取学生列表: skip={skip}, limit={limit}, 返回{len(students)}条记录")
    return students

# 创建新学生
@app.post("/api/students", response_model=schemas.Student)
async def create_student(
    student: schemas.StudentCreate,
    db: Session = Depends(get_db_session),
    current_user: models.AdminUser = Depends(get_current_admin_user)
):
    """创建新的学生记录"""
    # 检查学号是否已存在
    existing_student = crud.validate_student_id(db, student.student_id)
    if existing_student:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"学号 {student.student_id} 已存在"
        )
    
    # 创建学生
    try:
        new_student = crud.create_student(db, student)
        return new_student
    except Exception as e:
        logger.error(f"创建学生失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建学生失败: {str(e)}"
        )

# 获取单个学生
@app.get("/api/students/{student_id}", response_model=schemas.Student)
async def get_student(
    student_id: str,
    db: Session = Depends(get_db_session),
    current_user: models.AdminUser = Depends(get_current_admin_user)
):
    student = crud.get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="学生未找到")
    return student

# 更新学生信息
@app.put("/api/students/{student_id}", response_model=schemas.Student)
async def update_student(
    student_id: str,
    student_update: schemas.StudentUpdate,
    db: Session = Depends(get_db_session),
    current_user: models.AdminUser = Depends(get_current_admin_user)
):
    updated_student = crud.update_student(db, student_id, student_update)
    if not updated_student:
        raise HTTPException(status_code=404, detail="学生未找到")
    return updated_student

# 删除学生
@app.delete("/api/students/{student_id}")
async def delete_student(
    student_id: str,
    db: Session = Depends(get_db_session),
    current_user: models.AdminUser = Depends(get_current_admin_user)
):
    if not crud.delete_student(db, student_id):
        raise HTTPException(status_code=404, detail="学生未找到")
    return {"detail": "删除成功"}

# 学号校验（带缓存）
@app.post("/api/students/validate", response_model=Optional[schemas.Student])
async def validate_student(
    request: schemas.StudentIDRequest,
    db: Session = Depends(get_db_session)
):
    # 使用缓存提高性能
    from utils.cache import get_cached_student, cache_student
    
    # 先尝试从缓存获取
    cached_student = get_cached_student(request.student_id)
    if cached_student:
        return cached_student
    
    # 缓存未命中，查询数据库
    student = crud.validate_student_id(db, request.student_id)
    if not student:
        # 学号不存在时返回None，不抛出错误（这是正常的新增情况）
        return None
    
    # 缓存结果（120秒）
    cache_student(request.student_id, student, ttl=120)
    return student

# 获取学生信息（用于检测记录详情）
@app.get("/api/students/info/{student_id}", response_model=Optional[schemas.Student])
async def get_student_info(
    student_id: str,
    db: Session = Depends(get_db_session),
    current_user: models.AdminUser = Depends(get_current_admin_user)
):
    student = crud.get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="学生未找到")
    return student

# 报告相关API
@app.get("/api/reports/{student_id}")
async def get_report(student_id: str, db: Session = Depends(get_db_session)):
    try:
        from services.report_service import generate_report_content
        logger.info(f"开始生成报告，学号: {student_id}")
        content = generate_report_content(db, student_id)
        logger.info(f"报告生成成功，学号: {student_id}")
        return {"content": content}
    except ValueError as e:
        error_msg = str(e)
        logger.warning(f"生成报告时出现ValueError，学号: {student_id}, 错误: {error_msg}")
        # 如果学生不存在，返回404
        if "not found" in error_msg.lower() or "Student not found" in error_msg:
            raise HTTPException(status_code=404, detail=error_msg)
        # 其他ValueError（如没有检测记录）也返回内容，但状态码为200
        return {"content": error_msg}
    except Exception as e:
        logger.error(f"生成报告时出现未预期的错误，学号: {student_id}, 错误: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"生成报告失败: {str(e)}")

@app.get("/api/reports/{student_id}/download")
async def download_report(
    student_id: str,
    format: str = "pdf",
    db: Session = Depends(get_db_session)
):
    try:
        from services.report_service import generate_report_content, generate_pdf_report, generate_excel_report
        # 生成报告内容
        content = generate_report_content(db, student_id)
        
        # 获取学生信息
        student = crud.get_student(db, student_id)
        student_name = student.name if student else "Student"
        
        # 根据格式生成对应文件
        if format == "pdf":
            filepath = generate_pdf_report(content, student_id, student_name)
        elif format == "excel":
            filepath = generate_excel_report(db, student_id)
        else:
            raise HTTPException(status_code=400, detail="Invalid format. Use 'pdf' or 'excel'.")
        
        # 检查文件是否存在
        if not os.path.exists(filepath):
            raise HTTPException(status_code=500, detail="Report generation failed")
        
        # 返回文件下载
        return FileResponse(
            path=filepath,
            filename=os.path.basename(filepath),
            media_type="application/octet-stream"
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation error: {str(e)}")

# 仪表板API接口（优化版，使用聚合查询和缓存）
@app.get("/api/dashboard/stats", summary="获取仪表板统计数据")
async def get_dashboard_stats(
    db: Session = Depends(get_db_session),
    current_user: models.AdminUser = Depends(get_current_admin_user)
):
    """获取仪表板所需的统计数据"""
    try:
        # 使用缓存提高性能
        from utils.cache import get_cached_stats, cache_stats
        
        # 先尝试从缓存获取
        cached_stats = get_cached_stats("dashboard_stats")
        if cached_stats:
            return cached_stats
        
        # 使用聚合查询替代全表扫描
        stats = crud.get_dashboard_stats_aggregated(db)
        
        # 缓存结果（60秒）
        cache_stats("dashboard_stats", stats, ttl=60)
        
        return stats
    except Exception as e:
        logger.error(f"获取统计数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取统计数据失败: {str(e)}")

@app.get("/api/dashboard/trend", summary="获取检测趋势数据")
async def get_trend_data(
    days: int = 7,
    db: Session = Depends(get_db_session),
    current_user: models.AdminUser = Depends(get_current_admin_user)
):
    """获取指定天数内的检测趋势数据"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        records = crud.get_test_records(
            db, 
            start_time=start_date, 
            end_time=end_date, 
            skip=0, 
            limit=999999
        )
        
        # 按日期分组统计
        trend_data = {}
        for record in records:
            date_key = record.test_time.strftime('%Y-%m-%d')
            trend_data[date_key] = trend_data.get(date_key, 0) + 1
        
        # 生成连续日期的数据
        dates = []
        values = []
        current_date = start_date
        
        while current_date <= end_date:
            date_key = current_date.strftime('%Y-%m-%d')
            dates.append(date_key)
            values.append(trend_data.get(date_key, 0))
            current_date += timedelta(days=1)
        
        return {
            "dates": dates,
            "values": values
        }
    except Exception as e:
        logger.error(f"获取趋势数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取趋势数据失败: {str(e)}")

@app.get("/api/dashboard/score-stats", summary="获取问卷得分统计")
async def get_score_stats(
    limit: int = 100,
    db: Session = Depends(get_db_session),
    current_user: models.AdminUser = Depends(get_current_admin_user)
):
    """获取问卷得分统计数据"""
    try:
        records = crud.get_test_records(db, skip=0, limit=limit)
        
        score_stats = {
            "焦虑": [],
            "抑郁": [],
            "压力": []
        }
        
        for record in records:
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
        
        return score_distribution
    except Exception as e:
        logger.error(f"获取得分统计失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取得分统计失败: {str(e)}")

@app.get("/api/dashboard/class-distribution", summary="获取班级分布数据")
async def get_class_distribution(
    db: Session = Depends(get_db_session),
    current_user: models.AdminUser = Depends(get_current_admin_user)
):
    """获取班级学生分布数据"""
    try:
        students = crud.get_students_with_filters(db, skip=0, limit=999999)
        
        class_distribution = {}
        for student in students:
            class_name = student.class_name
            class_distribution[class_name] = class_distribution.get(class_name, 0) + 1
        
        return class_distribution
    except Exception as e:
        logger.error(f"获取班级分布失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取班级分布失败: {str(e)}")

# === 数据导出接口 ===

@app.get("/api/export/students", summary="导出学生数据")
async def export_students(
    skip: int = 0,
    limit: int = 10000,
    db: Session = Depends(get_db_session),
    current_user: models.AdminUser = Depends(get_current_admin_user)
):
    """导出学生数据到Excel文件"""
    try:
        filepath = crud.export_students_to_excel(db, skip=skip, limit=limit)
        
        # 返回文件下载
        import aiofiles
        from fastapi.responses import FileResponse
        
        filename = os.path.basename(filepath)
        return FileResponse(
            filepath,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            filename=filename
        )
    except Exception as e:
        logger.error(f"导出学生数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"导出学生数据失败: {str(e)}")


@app.get("/api/export/test-records", summary="导出检测记录数据")
async def export_test_records(
    user_id: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    is_abnormal: Optional[bool] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db_session),
    current_user: models.AdminUser = Depends(get_current_admin_user)
):
    """导出检测记录数据到Excel文件"""
    try:
        filepath = crud.export_test_records_to_excel(
            db, 
            user_id=user_id, 
            start_time=start_time, 
            end_time=end_time,
            is_abnormal=is_abnormal,
            status=status
        )
        
        # 返回文件下载
        import aiofiles
        from fastapi.responses import FileResponse
        
        filename = os.path.basename(filepath)
        return FileResponse(
            filepath,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            filename=filename
        )
    except Exception as e:
        logger.error(f"导出检测记录数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"导出检测记录数据失败: {str(e)}")


@app.get("/api/export/dashboard-stats", summary="导出仪表板统计数据")
async def export_dashboard_stats(
    db: Session = Depends(get_db_session),
    current_user: models.AdminUser = Depends(get_current_admin_user)
):
    """导出仪表板统计数据到Excel文件"""
    try:
        filepath = crud.export_dashboard_stats_to_excel(db)
        
        # 返回文件下载
        import aiofiles
        from fastapi.responses import FileResponse
        
        filename = os.path.basename(filepath)
        return FileResponse(
            filepath,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            filename=filename
        )
    except Exception as e:
        logger.error(f"导出仪表板统计数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"导出仪表板统计数据失败: {str(e)}")

# === 第一阶段：客户端对接接口 ===

@app.get("/api/students/{student_id}", response_model=schemas.Student, summary="获取学生信息")
async def get_student_info(
    student_id: str,
    db: Session = Depends(get_db_session),
    current_user: models.AdminUser = Depends(get_current_admin_user)
):
    """获取指定学号的学生信息"""
    student = crud.get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="学生未找到")
    return student

@app.post("/api/students/batch-query", summary="批量查询学生信息")
async def batch_query_students(
    query: schemas.StudentBatchQuery,
    db: Session = Depends(get_db_session),
    current_user: models.AdminUser = Depends(get_current_admin_user)
):
    """批量查询学生信息"""
    students = []
    for student_id in query.student_ids:
        student = crud.get_student(db, student_id)
        if student:
            students.append(student)
    
    return {"students": students, "total_count": len(students)}

@app.get("/api/test-records/status/{student_id}", summary="获取学生检测记录状态")
async def get_student_test_status(
    student_id: str,
    db: Session = Depends(get_db_session),
    current_user: models.AdminUser = Depends(get_current_admin_user)
):
    """获取指定学生的检测记录状态"""
    try:
        status_data = crud.get_student_test_records_status(db, student_id)
        return status_data
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"获取学生检测状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取学生检测状态失败: {str(e)}")

@app.get("/api/test-records/batch-status", summary="批量获取检测记录状态")
async def batch_get_test_status(
    student_ids: Optional[List[str]] = None,
    db: Session = Depends(get_db_session),
    current_user: models.AdminUser = Depends(get_current_admin_user)
):
    """批量获取检测记录状态"""
    try:
        status_data = crud.get_test_records_batch_status(db, student_ids)
        return status_data
    except Exception as e:
        logger.error(f"批量获取检测状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"批量获取检测状态失败: {str(e)}")

@app.put("/api/test-records/{record_id}/status", summary="更新检测记录状态")
async def update_test_record_status(
    record_id: int,
    status_update: schemas.TestRecordStatusUpdate,
    db: Session = Depends(get_db_session),
    current_user: models.AdminUser = Depends(get_current_admin_user)
):
    """更新指定检测记录的状态"""
    try:
        updated_record = crud.update_test_record_status(db, record_id, status_update)
        if not updated_record:
            raise HTTPException(status_code=404, detail="检测记录未找到")
        return {"message": "状态更新成功", "record": updated_record}
    except Exception as e:
        logger.error(f"更新检测记录状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新检测记录状态失败: {str(e)}")

# 批量生成报告API
@app.post("/api/test-records/batch-generate-reports", summary="批量生成报告")
async def batch_generate_reports(
    request: schemas.BatchGenerateReportsRequest,
    db: Session = Depends(get_db_session),
    current_user: models.AdminUser = Depends(get_current_admin_user)
):
    """批量生成指定检测记录的报告"""
    try:
        record_ids = request.record_ids
        format = request.format
        
        if not record_ids:
            raise HTTPException(status_code=400, detail="请提供要生成报告的记录ID列表")
        
        if format not in ["pdf", "excel"]:
            raise HTTPException(status_code=400, detail="格式参数必须是 'pdf' 或 'excel'")
        
        # 获取所有记录
        records = []
        for record_id in record_ids:
            record = crud.get_test_record_detail(db, record_id)
            if not record:
                raise HTTPException(status_code=404, detail=f"检测记录 {record_id} 未找到")
            records.append(record)
        
        # 生成报告文件列表
        from services.report_service import generate_report_content, generate_pdf_report, generate_excel_report
        report_files = []
        for record in records:
            try:
                # 生成报告内容
                content = generate_report_content(db, record.student.student_id)
                
                # 获取学生姓名
                student_name = record.student.name if record.student else "Student"
                
                # 根据格式生成对应文件
                if format == "pdf":
                    filepath = generate_pdf_report(content, record.student.student_id, student_name)
                elif format == "excel":
                    filepath = generate_excel_report(db, record.student.student_id)
                
                # 检查文件是否存在
                if os.path.exists(filepath):
                    report_files.append({
                        "record_id": record.id,
                        "student_id": record.student.student_id,
                        "file_path": filepath,
                        "file_name": os.path.basename(filepath)
                    })
            except Exception as e:
                logger.error(f"为记录 {record.id} 生成报告失败: {e}")
                continue
        
        return {
            "message": f"成功生成 {len(report_files)} 份报告",
            "report_files": report_files,
            "failed_count": len(record_ids) - len(report_files)
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"批量生成报告失败: {e}")
        raise HTTPException(status_code=500, detail=f"批量生成报告失败: {str(e)}")

# === 客户端对接接口 ===

@app.post("/api/client/validate-student", response_model=schemas.StudentValidateResponse, summary="客户端学号验证")
async def validate_student_for_client(
    request: schemas.StudentValidateRequest,
    db: Session = Depends(get_db_session)
):
    """客户端学号验证，返回学生基本信息"""
    try:
        result = crud.validate_student_for_client(db, request.student_id)
        return result
    except Exception as e:
        logger.error(f"学号验证失败: {e}")
        raise HTTPException(status_code=500, detail=f"学号验证失败: {str(e)}")

@app.post("/api/client/upload-test-data", response_model=schemas.TestRecordDetail, summary="客户端上传检测数据")
async def upload_test_data_from_client(
    pdf_file: UploadFile = File(...),
    test_data: str = Form(...),
    db: Session = Depends(get_db_session)
):
    """接收客户端上传的检测数据和PDF文件"""
    try:
        # 解析JSON字符串
        import json
        test_data_dict = json.loads(test_data)
        test_data_obj = schemas.ClientTestDataUpload(**test_data_dict)
        
        # 创建PDF文件存储目录（按日期分目录）
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        pdf_dir = os.path.join(settings.REPORT_DIR, today)
        os.makedirs(pdf_dir, exist_ok=True)
        
        # 生成PDF文件名（格式：姓名_学号.pdf）
        # 如果name为None，使用student_id作为文件名
        if test_data_obj.name:
            safe_name = "".join(c for c in test_data_obj.name if c.isalnum() or c in (" ", "-", "_"))
            pdf_filename = f"{safe_name}_{test_data_obj.student_id}.pdf"
        else:
            pdf_filename = f"{test_data_obj.student_id}.pdf"
        pdf_filepath = os.path.join(pdf_dir, pdf_filename)
        
        # 检查文件大小限制
        content = await pdf_file.read()
        if len(content) > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
            raise HTTPException(
                status_code=413, 
                detail=f"文件大小超过限制 ({settings.MAX_FILE_SIZE_MB}MB)"
            )
        
        # 保存PDF文件
        try:
            with open(pdf_filepath, "wb") as buffer:
                buffer.write(content)
            logger.info(f"PDF文件已保存: {pdf_filepath}")
        except Exception as e:
            logger.error(f"保存PDF文件失败: {e}")
            raise HTTPException(status_code=500, detail=f"保存PDF文件失败: {str(e)}")
        
        # 存储检测数据
        db_test_record = crud.create_client_test_data(db, test_data_obj, pdf_filepath)
        
        logger.info(f"成功接收并存储客户端检测数据，学生ID: {test_data_obj.student_id}")
        return db_test_record
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"处理客户端检测数据上传失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"数据上传失败: {str(e)}"
        )

@app.get("/api/client/test-status/{student_id}", response_model=schemas.TestStatusResponse, summary="查询学生检测状态")
async def get_student_test_status(
    student_id: str,
    db: Session = Depends(get_db_session)
):
    """查询学生检测状态"""
    try:
        status_info = crud.get_student_test_status_for_client(db, student_id)
        return status_info
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"获取学生检测状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取学生检测状态失败: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
