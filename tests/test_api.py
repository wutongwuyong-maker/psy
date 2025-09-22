import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_import():
    try:
        from psy_admin_fastapi.main import app
        print("导入成功")
        assert True
    except ImportError as e:
        print(f"导入失败: {e}")
        assert False, f"导入失败: {e}"
