"""Add foreign keys and indexes

Revision ID: 38e3594ee081
Revises: 
Create Date: 2025-09-20 20:02:58.422093

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '38e3594ee081'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 为tests表添加外键约束（如果不存在）
    try:
        op.create_foreign_key(
            'fk_tests_student_id', 
            'tests', 
            'students', 
            ['student_fk_id'], 
            ['id']
        )
    except Exception:
        # 外键可能已存在，忽略错误
        pass
    
    # 为tests表添加索引
    op.create_index('ix_tests_test_time', 'tests', ['test_time'])
    op.create_index('ix_tests_status', 'tests', ['status'])
    op.create_index('ix_tests_student_fk_id', 'tests', ['student_fk_id'])
    
    # 为scores表添加索引
    op.create_index('ix_scores_test_fk_id', 'scores', ['test_fk_id'])
    
    # 为physiological_data表添加索引
    op.create_index('ix_physiological_data_test_fk_id', 'physiological_data', ['test_fk_id'])
    
    # 为students表的student_id添加唯一索引（如果不存在）
    try:
        op.create_unique_constraint('uq_students_student_id', 'students', ['student_id'])
    except Exception:
        # 唯一约束可能已存在，忽略错误
        pass


def downgrade() -> None:
    # 删除索引
    op.drop_index('ix_physiological_data_test_fk_id', 'physiological_data')
    op.drop_index('ix_scores_test_fk_id', 'scores')
    op.drop_index('ix_tests_student_fk_id', 'tests')
    op.drop_index('ix_tests_status', 'tests')
    op.drop_index('ix_tests_test_time', 'tests')
    
    # 删除外键约束
    try:
        op.drop_constraint('fk_tests_student_id', 'tests', type_='foreignkey')
    except Exception:
        pass
    
    # 删除唯一约束
    try:
        op.drop_constraint('uq_students_student_id', 'students', type_='unique')
    except Exception:
        pass
