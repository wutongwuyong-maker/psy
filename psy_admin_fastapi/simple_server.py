import sys
import os
import time
import signal

# 设置信号处理函数，让程序能够优雅地退出
def signal_handler(sig, frame):
    print("\n正在关闭服务器...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import uvicorn
    from main import app
    
    print("正在启动服务器...")
    print("服务器将在 http://127.0.0.1:8000 上运行")
    print("按 Ctrl+C 停止服务器")
    
    # 启动服务器
    uvicorn.run(
        app, 
        host="127.0.0.1", 
        port=8000, 
        log_level="info", 
        reload=False, 
        access_log=False,
        use_colors=False
    )
except Exception as e:
    print(f"启动服务器时出错: {e}")
    import traceback
    traceback.print_exc()