from psy_admin_fastapi.database import engine
from sqlalchemy import text

def fix_tests_table():
    """修复tests表结构，删除user_fk_id字段，保留student_fk_id字段"""
    with engine.connect() as conn:
        try:
            # 检查是否存在user_fk_id字段
            has_user_fk_id = conn.execute(
                text(
                    """
                    SELECT COUNT(*)
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = DATABASE()
                      AND TABLE_NAME = 'tests'
                      AND COLUMN_NAME = 'user_fk_id'
                    """
                )
            ).scalar() or 0

            if has_user_fk_id:
                print("发现user_fk_id字段，正在删除...")
                
                # 首先删除外键约束
                try:
                    conn.execute(text("ALTER TABLE tests DROP FOREIGN KEY tests_ibfk_1"))
                    print("已删除外键约束tests_ibfk_1")
                except Exception as e:
                    print(f"删除外键约束时出错: {e}")
                
                # 删除user_fk_id字段
                conn.execute(text("ALTER TABLE tests DROP COLUMN user_fk_id"))
                print("已删除user_fk_id字段")
            else:
                print("未发现user_fk_id字段，无需修复")

            # 检查是否存在student_fk_id字段
            has_student_fk_id = conn.execute(
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

            if not has_student_fk_id:
                print("未发现student_fk_id字段，正在添加...")
                # 添加student_fk_id字段
                conn.execute(text("ALTER TABLE tests ADD COLUMN student_fk_id INT NOT NULL"))
                print("已添加student_fk_id字段")
            else:
                print("已存在student_fk_id字段，无需添加")

            # 添加外键约束
            try:
                conn.execute(text("ALTER TABLE tests ADD CONSTRAINT fk_tests_student_id FOREIGN KEY (student_fk_id) REFERENCES students(id)"))
                print("已添加外键约束fk_tests_student_id")
            except Exception as e:
                print(f"添加外键约束时出错: {e}")

            # 提交事务
            conn.commit()
            print("表结构修复完成")

        except Exception as e:
            print(f"修复过程中出现错误: {e}")
            conn.rollback()

if __name__ == "__main__":
    fix_tests_table()