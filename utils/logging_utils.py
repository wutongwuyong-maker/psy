#!/usr/bin/env python3
"""
日志记录工具
"""
import logging
import sys
import os
from datetime import datetime
from typing import Optional, Dict, Any
from functools import wraps
import json

# 配置日志格式
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

class OperationLogger:
    """操作日志记录器"""
    
    def __init__(self, name: str = "operation_logger"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # 如果还没有处理器，添加处理器
        if not self.logger.handlers:
            # 创建文件处理器
            file_handler = logging.FileHandler('operations.log', encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            file_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
            file_handler.setFormatter(file_formatter)
            
            # 创建控制台处理器
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            console_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
            console_handler.setFormatter(console_formatter)
            
            # 添加处理器
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def log_user_operation(self, user_id: str, operation: str, details: Dict[str, Any] = None):
        """记录用户操作"""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "operation": operation,
            "details": details or {}
        }
        self.logger.info(f"用户操作: {json.dumps(log_data, ensure_ascii=False)}")
    
    def log_api_request(self, endpoint: str, method: str, user_id: str = None, 
                       params: Dict[str, Any] = None, response_code: int = None):
        """记录API请求"""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "endpoint": endpoint,
            "method": method,
            "user_id": user_id,
            "params": params or {},
            "response_code": response_code
        }
        self.logger.info(f"API请求: {json.dumps(log_data, ensure_ascii=False)}")
    
    def log_error(self, error_type: str, error_message: str, details: Dict[str, Any] = None):
        """记录错误"""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "error_type": error_type,
            "error_message": error_message,
            "details": details or {}
        }
        self.logger.error(f"错误: {json.dumps(log_data, ensure_ascii=False)}")
    
    def log_database_operation(self, operation: str, table: str, record_id: str = None, 
                              success: bool = True, error: str = None):
        """记录数据库操作"""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "table": table,
            "record_id": record_id,
            "success": success,
            "error": error
        }
        if success:
            self.logger.info(f"数据库操作: {json.dumps(log_data, ensure_ascii=False)}")
        else:
            self.logger.error(f"数据库操作失败: {json.dumps(log_data, ensure_ascii=False)}")
    
    def log_file_operation(self, operation: str, file_path: str, file_size: int = None, 
                         success: bool = True, error: str = None):
        """记录文件操作"""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "file_path": file_path,
            "file_size": file_size,
            "success": success,
            "error": error
        }
        if success:
            self.logger.info(f"文件操作: {json.dumps(log_data, ensure_ascii=False)}")
        else:
            self.logger.error(f"文件操作失败: {json.dumps(log_data, ensure_ascii=False)}")

class AuditLogger:
    """审计日志记录器"""
    
    def __init__(self, name: str = "audit_logger"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # 如果还没有处理器，添加处理器
        if not self.logger.handlers:
            # 创建文件处理器
            file_handler = logging.FileHandler('audit.log', encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            file_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
            file_handler.setFormatter(file_formatter)
            
            # 添加处理器
            self.logger.addHandler(file_handler)
    
    def log_login_attempt(self, username: str, success: bool, ip_address: str, 
                        user_agent: str = None, error_message: str = None):
        """记录登录尝试"""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "username": username,
            "success": success,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "error_message": error_message
        }
        if success:
            self.logger.info(f"登录成功: {json.dumps(log_data, ensure_ascii=False)}")
        else:
            self.logger.warning(f"登录失败: {json.dumps(log_data, ensure_ascii=False)}")
    
    def log_data_access(self, user_id: str, data_type: str, data_id: str, 
                       operation: str, ip_address: str):
        """记录数据访问"""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "data_type": data_type,
            "data_id": data_id,
            "operation": operation,
            "ip_address": ip_address
        }
        self.logger.info(f"数据访问: {json.dumps(log_data, ensure_ascii=False)}")
    
    def log_permission_change(self, admin_id: str, target_user: str, 
                            permission_type: str, action: str, old_value: str, 
                            new_value: str, ip_address: str):
        """记录权限变更"""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "admin_id": admin_id,
            "target_user": target_user,
            "permission_type": permission_type,
            "action": action,
            "old_value": old_value,
            "new_value": new_value,
            "ip_address": ip_address
        }
        self.logger.info(f"权限变更: {json.dumps(log_data, ensure_ascii=False)}")
    
    def log_system_event(self, event_type: str, event_details: Dict[str, Any], 
                        ip_address: str = None):
        """记录系统事件"""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "event_details": event_details,
            "ip_address": ip_address
        }
        self.logger.info(f"系统事件: {json.dumps(log_data, ensure_ascii=False)}")

class PerformanceLogger:
    """性能日志记录器"""
    
    def __init__(self, name: str = "performance_logger"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # 如果还没有处理器，添加处理器
        if not self.logger.handlers:
            # 创建文件处理器
            file_handler = logging.FileHandler('performance.log', encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            file_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
            file_handler.setFormatter(file_formatter)
            
            # 添加处理器
            self.logger.addHandler(file_handler)
    
    def log_api_performance(self, endpoint: str, method: str, duration: float, 
                           response_size: int = None, user_id: str = None):
        """记录API性能"""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "endpoint": endpoint,
            "method": method,
            "duration_ms": round(duration * 1000, 2),
            "response_size": response_size,
            "user_id": user_id
        }
        self.logger.info(f"API性能: {json.dumps(log_data, ensure_ascii=False)}")
    
    def log_database_performance(self, operation: str, table: str, duration: float, 
                               rows_affected: int = None):
        """记录数据库性能"""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "table": table,
            "duration_ms": round(duration * 1000, 2),
            "rows_affected": rows_affected
        }
        self.logger.info(f"数据库性能: {json.dumps(log_data, ensure_ascii=False)}")
    
    def log_file_performance(self, operation: str, file_path: str, duration: float, 
                           file_size: int = None):
        """记录文件操作性能"""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "file_path": file_path,
            "duration_ms": round(duration * 1000, 2),
            "file_size": file_size
        }
        self.logger.info(f"文件性能: {json.dumps(log_data, ensure_ascii=False)}")

# 全局日志实例
operation_logger = OperationLogger()
audit_logger = AuditLogger()
performance_logger = PerformanceLogger()

def log_user_operation(operation: str):
    """用户操作装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 获取用户ID（假设在kwargs中）
            user_id = kwargs.get('user_id') or kwargs.get('current_user', {}).get('username', 'anonymous')
            
            # 记录操作开始
            operation_logger.log_user_operation(user_id, operation, {
                "function": func.__name__,
                "args_count": len(args),
                "kwargs_count": len(kwargs)
            })
            
            try:
                result = func(*args, **kwargs)
                # 记录操作成功
                operation_logger.log_user_operation(user_id, f"{operation}_success", {
                    "function": func.__name__,
                    "result_type": type(result).__name__
                })
                return result
            except Exception as e:
                # 记录操作失败
                operation_logger.log_user_operation(user_id, f"{operation}_failed", {
                    "function": func.__name__,
                    "error": str(e),
                    "error_type": type(e).__name__
                })
                raise
        return wrapper
    return decorator

def log_api_request(endpoint: str, method: str):
    """API请求装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = datetime.now()
            
            # 记录请求开始
            operation_logger.log_api_request(
                endpoint, method, 
                kwargs.get('user_id'), 
                kwargs.get('params')
            )
            
            try:
                result = func(*args, **kwargs)
                duration = (datetime.now() - start_time).total_seconds()
                
                # 记录请求成功
                operation_logger.log_api_request(
                    endpoint, method,
                    kwargs.get('user_id'),
                    kwargs.get('params'),
                    200
                )
                
                # 记录性能
                performance_logger.log_api_performance(
                    endpoint, method, duration,
                    len(str(result)) if result else 0,
                    kwargs.get('user_id')
                )
                
                return result
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds()
                
                # 记录请求失败
                operation_logger.log_api_request(
                    endpoint, method,
                    kwargs.get('user_id'),
                    kwargs.get('params'),
                    500
                )
                
                # 记录错误
                operation_logger.log_error("API_ERROR", str(e), {
                    "endpoint": endpoint,
                    "method": method,
                    "function": func.__name__
                })
                
                raise
        return wrapper
    return decorator

def log_database_operation(operation: str, table: str):
    """数据库操作装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = datetime.now()
            record_id = kwargs.get('record_id') or kwargs.get('id')
            
            try:
                result = func(*args, **kwargs)
                duration = (datetime.now() - start_time).total_seconds()
                
                # 记录操作成功
                operation_logger.log_database_operation(
                    operation, table, record_id, True
                )
                
                # 记录性能
                performance_logger.log_database_performance(
                    operation, table, duration,
                    getattr(result, 'count', None) if hasattr(result, 'count') else None
                )
                
                return result
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds()
                
                # 记录操作失败
                operation_logger.log_database_operation(
                    operation, table, record_id, False, str(e)
                )
                
                # 记录错误
                operation_logger.log_error("DATABASE_ERROR", str(e), {
                    "operation": operation,
                    "table": table,
                    "function": func.__name__
                })
                
                raise
        return wrapper
    return decorator

def log_file_operation(operation: str):
    """文件操作装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = datetime.now()
            file_path = kwargs.get('file_path') or args[0] if args else None
            
            try:
                result = func(*args, **kwargs)
                duration = (datetime.now() - start_time).total_seconds()
                
                # 记录操作成功
                operation_logger.log_file_operation(
                    operation, file_path, True
                )
                
                # 记录性能
                performance_logger.log_file_performance(
                    operation, file_path, duration
                )
                
                return result
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds()
                
                # 记录操作失败
                operation_logger.log_file_operation(
                    operation, file_path, False, str(e)
                )
                
                # 记录错误
                operation_logger.log_error("FILE_ERROR", str(e), {
                    "operation": operation,
                    "file_path": file_path,
                    "function": func.__name__
                })
                
                raise
        return wrapper
    return decorator

# 错误处理函数
def handle_database_error(func):
    """数据库错误处理装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # 记录数据库错误
            operation_logger.log_error("DATABASE_ERROR", str(e), {
                "function": func.__name__,
                "args": str(args),
                "kwargs": str(kwargs)
            })
            
            # 根据错误类型返回不同的错误信息
            if "duplicate key" in str(e).lower():
                raise ValueError("数据已存在，请检查重复项")
            elif "foreign key" in str(e).lower():
                raise ValueError("关联数据不存在，请检查数据完整性")
            elif "connection" in str(e).lower():
                raise ValueError("数据库连接失败，请稍后重试")
            else:
                raise ValueError("数据库操作失败，请稍后重试")
    return wrapper

def handle_api_error(func):
    """API错误处理装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # 记录API错误
            operation_logger.log_error("API_ERROR", str(e), {
                "function": func.__name__,
                "args": str(args),
                "kwargs": str(kwargs)
            })
            
            # 根据错误类型返回不同的错误信息
            if "validation" in str(e).lower():
                raise ValueError("数据验证失败，请检查输入格式")
            elif "authentication" in str(e).lower():
                raise ValueError("认证失败，请检查用户名和密码")
            elif "authorization" in str(e).lower():
                raise ValueError("权限不足，请联系管理员")
            else:
                raise ValueError("API请求失败，请稍后重试")
    return wrapper

def handle_file_error(func):
    """文件操作错误处理装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # 记录文件错误
            operation_logger.log_error("FILE_ERROR", str(e), {
                "function": func.__name__,
                "args": str(args),
                "kwargs": str(kwargs)
            })
            
            # 根据错误类型返回不同的错误信息
            if "not found" in str(e).lower():
                raise ValueError("文件不存在")
            elif "permission" in str(e).lower():
                raise ValueError("文件权限不足")
            elif "size" in str(e).lower():
                raise ValueError("文件大小超出限制")
            else:
                raise ValueError("文件操作失败，请稍后重试")
    return wrapper

# 初始化日志系统
def init_logging():
    """初始化日志系统"""
    # 确保日志目录存在
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 配置根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # 如果还没有处理器，添加处理器
    if not root_logger.handlers:
        # 创建文件处理器
        file_handler = logging.FileHandler(os.path.join(log_dir, 'app.log'), encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
        file_handler.setFormatter(file_formatter)
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
        console_handler.setFormatter(console_formatter)
        
        # 添加处理器
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
    
    return operation_logger, audit_logger, performance_logger

# 初始化日志系统
operation_logger, audit_logger, performance_logger = init_logging()
