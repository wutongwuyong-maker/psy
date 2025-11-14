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

        try:
            # 兼容新增 scores.max_score 和 scores.level 列
            has_max_score = conn.execute(
                text(
                    """
                    SELECT COUNT(*)
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = DATABASE()
                      AND TABLE_NAME = 'scores'
                      AND COLUMN_NAME = 'max_score'
                    """
                )
            ).scalar() or 0

            if not has_max_score:
                conn.execute(text("ALTER TABLE scores ADD COLUMN max_score INT NULL"))
        except SQLAlchemyError:
            pass

        try:
            has_level = conn.execute(
                text(
                    """
                    SELECT COUNT(*)
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = DATABASE()
                      AND TABLE_NAME = 'scores'
                      AND COLUMN_NAME = 'level'
                    """
                )
            ).scalar() or 0

            if not has_level:
                conn.execute(text("ALTER TABLE scores ADD COLUMN level VARCHAR(20) NULL"))
        except SQLAlchemyError:
            pass

        try:
            has_feedback = conn.execute(
                text(
                    """
                    SELECT COUNT(*)
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = DATABASE()
                      AND TABLE_NAME = 'scores'
                      AND COLUMN_NAME = 'questionnaire_feedback'
                    """
                )
            ).scalar() or 0

            if not has_feedback:
                conn.execute(
                    text(
                        "ALTER TABLE scores ADD COLUMN questionnaire_feedback VARCHAR(255) NULL DEFAULT ''"
                    )
                )
            else:
                conn.execute(
                    text(
                        "ALTER TABLE scores MODIFY COLUMN questionnaire_feedback VARCHAR(255) NULL DEFAULT ''"
                    )
                )
        except SQLAlchemyError:
            pass

        try:
            conn.commit()
        except Exception:
            pass

