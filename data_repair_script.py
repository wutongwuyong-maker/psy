#!/usr/bin/env python3
"""
数据修复脚本
用于扫描和修复孤儿记录、重复记录等数据问题
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from sqlalchemy.orm import Session
from sqlalchemy import text
from database import SessionLocal, engine
from models import Test, Student, Score, PhysiologicalData
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def scan_orphan_records():
    """扫描孤儿记录"""
    db = SessionLocal()
    try:
        # 扫描tests表中的孤儿记录
        orphan_tests = db.execute(text("""
            SELECT t.id, t.student_fk_id 
            FROM tests t 
            LEFT JOIN students s ON t.student_fk_id = s.id 
            WHERE s.id IS NULL
        """)).fetchall()
        
        # 扫描scores表中的孤儿记录
        orphan_scores = db.execute(text("""
            SELECT sc.id, sc.test_fk_id 
            FROM scores sc 
            LEFT JOIN tests t ON sc.test_fk_id = t.id 
            WHERE t.id IS NULL
        """)).fetchall()
        
        # 扫描physiological_data表中的孤儿记录
        orphan_physiological = db.execute(text("""
            SELECT pd.id, pd.test_fk_id 
            FROM physiological_data pd 
            LEFT JOIN tests t ON pd.test_fk_id = t.id 
            WHERE t.id IS NULL
        """)).fetchall()
        
        logger.info(f"发现孤儿记录:")
        logger.info(f"  - tests表: {len(orphan_tests)} 条")
        logger.info(f"  - scores表: {len(orphan_scores)} 条")
        logger.info(f"  - physiological_data表: {len(orphan_physiological)} 条")
        
        return {
            'orphan_tests': orphan_tests,
            'orphan_scores': orphan_scores,
            'orphan_physiological': orphan_physiological
        }
    finally:
        db.close()

def scan_duplicate_records():
    """扫描重复记录"""
    db = SessionLocal()
    try:
        # 扫描重复的student_id
        duplicate_students = db.execute(text("""
            SELECT student_id, COUNT(*) as count 
            FROM students 
            GROUP BY student_id 
            HAVING COUNT(*) > 1
        """)).fetchall()
        
        # 扫描重复的测试记录（同一学生在同一时间）
        duplicate_tests = db.execute(text("""
            SELECT student_fk_id, test_time, COUNT(*) as count 
            FROM tests 
            GROUP BY student_fk_id, test_time 
            HAVING COUNT(*) > 1
        """)).fetchall()
        
        logger.info(f"发现重复记录:")
        logger.info(f"  - students表: {len(duplicate_students)} 组重复")
        logger.info(f"  - tests表: {len(duplicate_tests)} 组重复")
        
        return {
            'duplicate_students': duplicate_students,
            'duplicate_tests': duplicate_tests
        }
    finally:
        db.close()

def generate_repair_sql(orphan_data, duplicate_data):
    """生成修复SQL语句"""
    repair_sql = []
    
    # 生成删除孤儿记录的SQL
    if orphan_data['orphan_tests']:
        test_ids = [str(record[0]) for record in orphan_data['orphan_tests']]
        repair_sql.append(f"-- 删除孤儿测试记录\nDELETE FROM tests WHERE id IN ({','.join(test_ids)});")
    
    if orphan_data['orphan_scores']:
        score_ids = [str(record[0]) for record in orphan_data['orphan_scores']]
        repair_sql.append(f"-- 删除孤儿分数记录\nDELETE FROM scores WHERE id IN ({','.join(score_ids)});")
    
    if orphan_data['orphan_physiological']:
        phys_ids = [str(record[0]) for record in orphan_data['orphan_physiological']]
        repair_sql.append(f"-- 删除孤儿生理数据记录\nDELETE FROM physiological_data WHERE id IN ({','.join(phys_ids)});")
    
    # 生成处理重复记录的SQL
    if duplicate_data['duplicate_students']:
        repair_sql.append("-- 处理重复学生记录（保留ID最小的）")
        for record in duplicate_data['duplicate_students']:
            student_id = record[0]
            repair_sql.append(f"""
DELETE s1 FROM students s1
INNER JOIN students s2 
WHERE s1.student_id = '{student_id}' 
  AND s1.student_id = s2.student_id 
  AND s1.id > s2.id;""")
    
    if duplicate_data['duplicate_tests']:
        repair_sql.append("-- 处理重复测试记录（保留ID最小的）")
        for record in duplicate_data['duplicate_tests']:
            student_fk_id = record[0]
            test_time = record[1]
            repair_sql.append(f"""
DELETE t1 FROM tests t1
INNER JOIN tests t2 
WHERE t1.student_fk_id = {student_fk_id} 
  AND t1.test_time = '{test_time}'
  AND t1.student_fk_id = t2.student_fk_id 
  AND t1.test_time = t2.test_time 
  AND t1.id > t2.id;""")
    
    return repair_sql

def execute_repair(repair_sql, dry_run=True):
    """执行修复操作"""
    if dry_run:
        logger.info("=== 修复SQL（预览模式）===")
        for sql in repair_sql:
            logger.info(sql)
        logger.info("=== 预览完成，未实际执行 ===")
        return
    
    db = SessionLocal()
    try:
        for sql in repair_sql:
            if sql.strip() and not sql.strip().startswith('--'):
                logger.info(f"执行SQL: {sql[:100]}...")
                db.execute(text(sql))
        
        db.commit()
        logger.info("修复操作完成")
    except Exception as e:
        db.rollback()
        logger.error(f"修复操作失败: {e}")
        raise
    finally:
        db.close()

def main():
    """主函数"""
    logger.info("开始数据修复扫描...")
    
    # 扫描数据问题
    orphan_data = scan_orphan_records()
    duplicate_data = scan_duplicate_records()
    
    # 生成修复SQL
    repair_sql = generate_repair_sql(orphan_data, duplicate_data)
    
    if not repair_sql:
        logger.info("未发现需要修复的数据问题")
        return
    
    # 执行修复（默认预览模式）
    execute_repair(repair_sql, dry_run=True)
    
    # 询问是否实际执行
    response = input("\n是否执行修复操作？(y/N): ")
    if response.lower() == 'y':
        execute_repair(repair_sql, dry_run=False)
    else:
        logger.info("修复操作已取消")

if __name__ == "__main__":
    main()

