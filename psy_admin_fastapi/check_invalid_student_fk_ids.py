from database import engine
from sqlalchemy import text

def check_invalid_student_fk_ids():
    """检查tests表中无效的student_fk_id值"""
    with engine.connect() as conn:
        try:
            # 查找tests表中student_fk_id不在students表中的记录
            result = conn.execute(
                text(
                    """
                    SELECT t.id, t.student_fk_id
                    FROM tests t
                    LEFT JOIN students s ON t.student_fk_id = s.id
                    WHERE s.id IS NULL
                    """
                )
            ).fetchall()
            
            if result:
                print(f"发现 {len(result)} 条记录的student_fk_id无效:")
                for row in result:
                    print(f"  Test ID: {row[0]}, student_fk_id: {row[1]}")
            else:
                print("所有记录的student_fk_id都有效")

        except Exception as e:
            print(f"检查过程中出现错误: {e}")

if __name__ == "__main__":
    check_invalid_student_fk_ids()