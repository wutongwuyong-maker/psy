# psy_admin_fastapi/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # 安全配置
    SECRET_KEY: str = "68dd6f3eb9a01eccbe048df7c0a4d5fcae00551a832680cfe98be5406b1ebaa6"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # 数据库配置
    DATABASE_URL_NO_DB: str = "mysql+pymysql://root:wzyis1204@localhost:3306/"
    DB_NAME: str = "psy_test_db"

    # 日志配置
    LOG_LEVEL: str = "INFO"

    # CORS配置
    ALLOWED_ORIGINS: str = "http://localhost:8080,http://127.0.0.1:8080"

    # 报告目录配置
    REPORT_DIR: str = "reports"

    # 文件上传限制
    MAX_FILE_SIZE_MB: int = 10

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
    @property
    def allowed_origins_list(self) -> list:
        """将ALLOWED_ORIGINS字符串转换为列表"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

settings = Settings()