from database import engine
from sqlalchemy import text

def fix_invalid_student_fk_ids():
    """修复tests表中无效的student_fk_id值"""
    with engine.connect() as conn:
        try:
            # 获取一个有效的学生ID
            result = conn.execute(text("SELECT id FROM students LIMIT 1")).fetchone()
            if not result:
                print("没有找到有效的学生记录，无法修复")
                return
            
            valid_student_id = result[0]
            print(f"使用有效学生ID: {valid_student_id} 进行修复")
            
            # 更新无效的student_fk_id
            update_result = conn.execute(
                text(
                    """
                    UPDATE tests t
                    SET t.student_fk_id = :valid_student_id
                    WHERE t.student_fk_id = 0
                    """
                ),
                {"valid_student_id": valid_student_id}
            )
            
            rows_updated = update_result.rowcount
            print(f"已更新 {rows_updated} 条记录")
            
            # 提交事务
            conn.commit()
            print("修复完成")
            
            # 现在添加外键约束
            try:
                conn.execute(text("ALTER TABLE tests ADD CONSTRAINT fk_tests_student_id FOREIGN KEY (student_fk_id) REFERENCES students(id)"))
                print("已添加外键约束fk_tests_student_id")
                conn.commit()
            except Exception as e:
                print(f"添加外键约束时出错: {e}")
                conn.rollback()

        except Exception as e:
            print(f"修复过程中出现错误: {e}")
            conn.rollback()

if __name__ == "__main__":
    fix_invalid_student_fk_ids()