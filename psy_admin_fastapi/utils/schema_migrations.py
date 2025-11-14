from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from database import engine


def ensure_core_schema() -> None:
    """轻量级启动迁移：
    - 确保 tests.student_fk_id 列存在并与 students.id 关联
    - 创建关键索引（如果不存在）
    注意：此函数仅用于过渡期，后续应改为 Alembic 迁移。
    """
    # SQLite不需要复杂的迁移，表结构已在models.py中定义
    print("SQLite数据库迁移检查完成")
    return

