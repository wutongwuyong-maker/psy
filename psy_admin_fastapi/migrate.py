#!/usr/bin/env python3
"""
数据库迁移管理脚本
提供便捷的迁移命令
"""

import sys
import os
import subprocess
import argparse

def run_alembic_command(command):
    """运行alembic命令"""
    try:
        result = subprocess.run(
            ["alembic"] + command.split(),
            cwd=os.path.dirname(__file__),
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
        if result.stderr:
            print("警告:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"命令执行失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False

def init_migration():
    """初始化迁移"""
    print("初始化Alembic迁移...")
    return run_alembic_command("revision --autogenerate -m 'Initial migration'")

def create_migration(message):
    """创建新迁移"""
    print(f"创建迁移: {message}")
    return run_alembic_command(f"revision -m '{message}'")

def upgrade_database(revision="head"):
    """升级数据库"""
    print(f"升级数据库到版本: {revision}")
    return run_alembic_command(f"upgrade {revision}")

def downgrade_database(revision):
    """降级数据库"""
    print(f"降级数据库到版本: {revision}")
    return run_alembic_command(f"downgrade {revision}")

def show_history():
    """显示迁移历史"""
    print("迁移历史:")
    return run_alembic_command("history")

def show_current():
    """显示当前版本"""
    print("当前数据库版本:")
    return run_alembic_command("current")

def main():
    parser = argparse.ArgumentParser(description="数据库迁移管理工具")
    parser.add_argument("command", choices=[
        "init", "create", "upgrade", "downgrade", "history", "current"
    ], help="要执行的命令")
    parser.add_argument("-m", "--message", help="迁移消息（用于create命令）")
    parser.add_argument("-r", "--revision", help="目标版本（用于upgrade/downgrade命令）")
    
    args = parser.parse_args()
    
    if args.command == "init":
        success = init_migration()
    elif args.command == "create":
        if not args.message:
            print("错误: create命令需要-m参数指定迁移消息")
            return 1
        success = create_migration(args.message)
    elif args.command == "upgrade":
        revision = args.revision or "head"
        success = upgrade_database(revision)
    elif args.command == "downgrade":
        if not args.revision:
            print("错误: downgrade命令需要-r参数指定目标版本")
            return 1
        success = downgrade_database(args.revision)
    elif args.command == "history":
        success = show_history()
    elif args.command == "current":
        success = show_current()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())

