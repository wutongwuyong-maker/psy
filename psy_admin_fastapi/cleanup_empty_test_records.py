#!/usr/bin/env python3
"""
清理空检测记录脚本
用于删除没有问卷得分和生理数据的空检测记录
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Test, Score, PhysiologicalData
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def cleanup_empty_test_records(dry_run: bool = True):
    """
    清理空的检测记录（没有问卷得分和生理数据的记录）
    
    Args:
        dry_run: 如果为True，只扫描不删除；如果为False，执行删除操作
    """
    db = SessionLocal()
    try:
        # 查询所有检测记录
        all_tests = db.query(Test).all()
        logger.info(f"总共找到 {len(all_tests)} 条检测记录")
        
        empty_records = []
        for test in all_tests:
            # 检查是否有问卷得分
            scores = db.query(Score).filter(Score.test_fk_id == test.id).all()
            # 检查是否有生理数据
            phys_data = db.query(PhysiologicalData).filter(PhysiologicalData.test_fk_id == test.id).all()
            
            # 如果既没有问卷得分也没有生理数据，则认为是空记录
            if not scores and not phys_data:
                empty_records.append(test)
                logger.info(f"发现空记录: ID={test.id}, 学生ID={test.student_fk_id}, "
                          f"检测时间={test.test_time}, 状态={test.status}")
        
        logger.info(f"共发现 {len(empty_records)} 条空检测记录")
        
        if dry_run:
            logger.info("【预览模式】不会实际删除记录。如需删除，请使用 --execute 参数")
            return len(empty_records)
        else:
            # 执行删除操作
            deleted_count = 0
            for test in empty_records:
                try:
                    db.delete(test)
                    deleted_count += 1
                    logger.info(f"已删除空记录: ID={test.id}")
                except Exception as e:
                    logger.error(f"删除记录 ID={test.id} 时出错: {str(e)}")
            
            # 提交事务
            db.commit()
            logger.info(f"成功删除 {deleted_count} 条空检测记录")
            return deleted_count
            
    except Exception as e:
        logger.error(f"清理过程中出错: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='清理空的检测记录')
    parser.add_argument('--execute', action='store_true', 
                       help='执行删除操作（默认只预览）')
    args = parser.parse_args()
    
    dry_run = not args.execute
    
    if dry_run:
        logger.info("=" * 60)
        logger.info("运行在预览模式，不会实际删除记录")
        logger.info("=" * 60)
    else:
        logger.info("=" * 60)
        logger.info("警告：将执行实际的删除操作！")
        logger.info("=" * 60)
        response = input("确认要继续吗？(yes/no): ")
        if response.lower() != 'yes':
            logger.info("操作已取消")
            return
    
    try:
        count = cleanup_empty_test_records(dry_run=dry_run)
        if dry_run:
            logger.info(f"\n预览完成：发现 {count} 条空记录")
            logger.info("如需删除这些记录，请使用 --execute 参数重新运行脚本")
        else:
            logger.info(f"\n清理完成：已删除 {count} 条空记录")
    except Exception as e:
        logger.error(f"脚本执行失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

