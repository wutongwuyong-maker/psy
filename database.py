# database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy_utils import database_exists, create_database # 新增导入


class Settings(BaseSettings):
    # 使用异步数据库驱动（asyncmy）替换同步驱动（pymysql）
    DATABASE_URL_NO_DB: str = "mysql+asyncmy://root:123456@localhost:3306/" # <<<<<< 异步驱动
    DB_NAME: str = "psy_test_db"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

# 数据库连接字符串（不包含具体数据库名，用于初步连接和创建数据库）
SQLALCHEMY_DATABASE_URL_NO_DB = settings.DATABASE_URL_NO_DB

# 完整的数据库连接字符串（包含数据库名，用于后续会话操作）
SQLALCHEMY_DATABASE_URL_FULL = settings.DATABASE_URL_NO_DB + settings.DB_NAME + "?charset=utf8mb4"

# 同步数据库连接字符串（使用 pymysql 驱动）
SQLALCHEMY_DATABASE_URL_SYNC = "mysql+pymysql://root:123456@localhost:3306/psy_test_db?charset=utf8mb4"

# 创建数据库引擎
# 初始引擎，用于连接到MySQL服务器，但不指定特定数据库
# 这样即使数据库不存在也不会报错
engine_no_db = create_engine(SQLALCHEMY_DATABASE_URL_NO_DB, echo=True)

# 完整异步引擎，连接到具体的数据库（配置连接池）
async_engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL_FULL,
    echo=True
)


# 创建同步数据库引擎（配置连接池）
engine = create_engine(
    SQLALCHEMY_DATABASE_URL_SYNC, 
    echo=True,
    pool_size=10,  # 连接池大小
    max_overflow=20,  # 最大溢出连接数
    pool_recycle=1800,  # 连接回收时间（30分钟）
    pool_pre_ping=True  # 连接前ping检查
)

# 创建同步会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 同步数据库依赖注入
def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=async_engine,
    class_=AsyncSession  # 指定异步会话类
)

# 异步数据库依赖注入（替换原有同步依赖）
async def get_db():
    async with AsyncSessionLocal() as db:
        try:
            yield db
            await db.commit()
        finally:
            await db.close()

# 创建一个基类，我们的数据库模型将继承自它
Base = declarative_base()

# 新增：用于确保数据库存在的函数
def create_database_if_not_exists():
    """
    检查数据库是否存在，如果不存在则创建它。
    这个函数可以在 FastAPI 的 startup_event 中调用。
    """
    if not database_exists(engine_no_db.url.render_as_string(hide_password=False) + settings.DB_NAME):
        # 注意：create_database 函数需要一个完整的URL来创建数据库
        # 这里我们拼接上数据库名
        create_database(engine_no_db.url.render_as_string(hide_password=False) + settings.DB_NAME)
        print(f"数据库 '{settings.DB_NAME}' 已创建。")
    else:
        print(f"数据库 '{settings.DB_NAME}' 已存在。")
