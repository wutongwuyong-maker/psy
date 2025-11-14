# database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy_utils import database_exists, create_database # 新增导入


class Settings(BaseSettings):
    # 使用SQLite数据库作为临时解决方案
    DATABASE_URL: str = "sqlite:///./psyadmin.db"
    DB_NAME: str = "psyadmin.db"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

# 数据库连接字符串
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# 创建数据库引擎
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    echo=True,
    connect_args={"check_same_thread": False}  # SQLite特有配置
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

# 创建一个基类，我们的数据库模型将继承自它
Base = declarative_base()

# 新增：用于确保数据库存在的函数
def create_database_if_not_exists():
    """
    SQLite不需要预先创建数据库，文件会在第一次连接时自动创建
    """
    print(f"使用SQLite数据库: {settings.DATABASE_URL}")
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    print("数据库表已创建")
