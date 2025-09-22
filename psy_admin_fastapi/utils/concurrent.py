import threading
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from typing import Callable, Any
from sqlalchemy.orm import Session
from psy_admin_fastapi.database import SessionLocal  # 导入数据库会话工厂

# 线程本地存储：用于保存每个线程的数据库会话
thread_local = threading.local()

class ThreadPoolManager:
    """ThreadPoolExecutor 单例管理器"""
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls._instance.executor = ThreadPoolExecutor(max_workers=4)
        return cls._instance

    def submit(self, func: Callable, *args, **kwargs) -> Any:
        """提交任务到线程池"""
        return self.executor.submit(func, *args, **kwargs)

    def shutdown(self, wait: bool = True):
        """关闭线程池"""
        self.executor.shutdown(wait=wait)

# 初始化线程池管理器
thread_pool = ThreadPoolManager()

def thread_safe_db(func: Callable) -> Callable:
    """线程安全的数据库操作装饰器：为每个线程创建独立的DB会话"""
    def wrapper(*args, **kwargs) -> Any:
        # 为当前线程创建独立的数据库会话
        if not hasattr(thread_local, "db"):
            thread_local.db = SessionLocal()
        
        try:
            # 将db会话注入到函数参数（如果函数接受db参数）
            if "db" in func.__code__.co_varnames:
                kwargs["db"] = thread_local.db
            return func(*args, **kwargs)
        finally:
            # 确保会话关闭（避免连接泄漏）
            if hasattr(thread_local, "db"):
                thread_local.db.close()
                del thread_local.db
    return wrapper

class TaskQueue:
    """简单的任务队列实现"""
    def __init__(self):
        self.queue = Queue()
        self.is_running = False

    def start(self):
        """启动任务队列消费线程"""
        if self.is_running:
            return
        self.is_running = True
        thread_pool.submit(self._process_tasks)

    def stop(self):
        """停止任务队列"""
        self.is_running = False

    def add_task(self, func: Callable, *args, **kwargs):
        """添加任务到队列"""
        self.queue.put((func, args, kwargs))

    def _process_tasks(self):
        """消费队列中的任务"""
        while self.is_running:
            try:
                func, args, kwargs = self.queue.get(timeout=1)
                thread_pool.submit(func, *args, **kwargs)
                self.queue.task_done()
            except Exception:
                continue

# 初始化全局任务队列
task_queue = TaskQueue()
