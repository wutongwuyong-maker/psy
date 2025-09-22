"""
缓存工具模块
提供简单的缓存装饰器功能
"""

from functools import wraps
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import time

# 全局缓存字典
_cache: Dict[str, Dict[str, Any]] = {}

def cached_query(ttl: int = 120):
    """
    缓存装饰器，用于缓存函数结果
    
    Args:
        ttl: 缓存存活时间（秒），默认120秒（2分钟）
    
    Returns:
        装饰器函数
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键：函数名 + 参数
            cache_key = f"{func.__name__}_{args}_{kwargs}"
            
            # 检查缓存是否存在且未过期
            if cache_key in _cache:
                cached_data = _cache[cache_key]
                cache_time = cached_data.get('timestamp')
                if cache_time and (datetime.now() - cache_time).seconds < ttl:
                    return cached_data['data']
            
            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            _cache[cache_key] = {
                'data': result,
                'timestamp': datetime.now()
            }
            
            return result
        
        return wrapper
    return decorator

def clear_cache():
    """清空所有缓存"""
    global _cache
    _cache.clear()

def get_cache_info() -> Dict[str, Any]:
    """获取缓存信息"""
    return {
        'cache_size': len(_cache),
        'cache_keys': list(_cache.keys()),
        'cache_timestamps': {key: value['timestamp'] for key, value in _cache.items()}
    }

def remove_cache_key(key: str) -> bool:
    """删除指定的缓存键"""
    if key in _cache:
        del _cache[key]
        return True
    return False

# 为了兼容性，提供一些常用的缓存操作
def set_cache(key: str, value: Any, ttl: Optional[int] = None):
    """设置缓存值"""
    _cache[key] = {
        'data': value,
        'timestamp': datetime.now()
    }

def get_cache(key: str) -> Any:
    """获取缓存值"""
    if key in _cache:
        return _cache[key]['data']
    return None

def has_cache(key: str) -> bool:
    """检查缓存是否存在"""
    return key in _cache


# 学生信息缓存
def cache_student(student_id: str, student_data: Any, ttl: int = 120):
    """缓存学生信息"""
    cache_key = f"student_{student_id}"
    _cache[cache_key] = {
        'data': student_data,
        'timestamp': datetime.now()
    }

def get_cached_student(student_id: str) -> Optional[Any]:
    """获取缓存的学生信息"""
    cache_key = f"student_{student_id}"
    if cache_key in _cache:
        cached_data = _cache[cache_key]
        cache_time = cached_data.get('timestamp')
        if cache_time and (datetime.now() - cache_time).seconds < 120:
            return cached_data['data']
    return None


# 统计数据缓存
def cache_stats(stats_key: str, stats_data: Any, ttl: int = 60):
    """缓存统计数据"""
    cache_key = f"stats_{stats_key}"
    _cache[cache_key] = {
        'data': stats_data,
        'timestamp': datetime.now()
    }

def get_cached_stats(stats_key: str) -> Optional[Any]:
    """获取缓存的统计数据"""
    cache_key = f"stats_{stats_key}"
    if cache_key in _cache:
        cached_data = _cache[cache_key]
        cache_time = cached_data.get('timestamp')
        if cache_time and (datetime.now() - cache_time).seconds < 60:
            return cached_data['data']
    return None