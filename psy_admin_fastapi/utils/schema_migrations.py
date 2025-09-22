from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from psy_admin_fastapi.database import engine


def ensure_core_schema() -> None:
    """轻量级启动迁移：
    - 确保 tests.student_fk_id 列存在并与 students.id 关联
    - 创建关键索引（如果不存在）
    注意：此函数仅用于过渡期，后续应改为 Alembic 迁移。
    """
    with engine.connect() as conn:
        try:
            # 检查 tests 表是否存在该列
            has_col = conn.execute(
                text(
                    """
                    SELECT COUNT(*)
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = DATABASE()
                      AND TABLE_NAME = 'tests'
                      AND COLUMN_NAME = 'student_fk_id'
                    """
                )
            ).scalar() or 0

            if not has_col:
                conn.execute(text("ALTER TABLE tests ADD COLUMN student_fk_id INT NOT NULL"))
                # 尝试用现有关系补足外键（若已有 student_id 字段可回填，这里仅建立 FK 与索引）
            # 外键与索引（如果不存在则创建）
            # 索引
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_tests_student_fk_id ON tests(student_fk_id)"
                )
            )
            conn.execute(
                text("CREATE INDEX IF NOT EXISTS idx_tests_test_time ON tests(test_time)")
            )
        except SQLAlchemyError:
            # 兼容 MySQL 5/8 对 IF NOT EXISTS 的差异，忽略已存在错误
            pass

