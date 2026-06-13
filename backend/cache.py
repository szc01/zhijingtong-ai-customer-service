"""
智净通智能客服系统 - 缓存模块
提供简单的内存缓存机制，优化重复查询性能
"""
from datetime import datetime, timedelta
from typing import Any, Optional, Dict
from functools import wraps
import hashlib
import threading


class SimpleCache:
    """
    简单的内存缓存类
    
    特点：
    - 线程安全
    - 支持过期时间
    - 支持最大容量限制
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        """
        初始化缓存
        
        Args:
            max_size: 最大缓存条目数
            default_ttl: 默认过期时间（秒）
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._lock = threading.Lock()
    
    def _generate_key(self, *args, **kwargs) -> str:
        """生成缓存键"""
        key_data = str(args) + str(kwargs)
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存值
        
        Args:
            key: 缓存键
            
        Returns:
            缓存值，如果不存在或已过期返回None
        """
        with self._lock:
            if key not in self._cache:
                return None
            
            entry = self._cache[key]
            if datetime.now() > entry["expires_at"]:
                del self._cache[key]
                return None
            
            return entry["value"]
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒），None使用默认值
        """
        with self._lock:
            # 如果超过最大容量，删除最旧的条目
            if len(self._cache) >= self._max_size:
                oldest_key = min(
                    self._cache.keys(),
                    key=lambda k: self._cache[k]["created_at"]
                )
                del self._cache[oldest_key]
            
            expires_at = datetime.now() + timedelta(
                seconds=ttl or self._default_ttl
            )
            
            self._cache[key] = {
                "value": value,
                "created_at": datetime.now(),
                "expires_at": expires_at
            }
    
    def delete(self, key: str) -> bool:
        """
        删除缓存
        
        Args:
            key: 缓存键
            
        Returns:
            是否成功删除
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def clear(self) -> None:
        """清空所有缓存"""
        with self._lock:
            self._cache.clear()
    
    def get_stats(self) -> dict:
        """
        获取缓存统计信息
        
        Returns:
            统计信息字典
        """
        with self._lock:
            valid_count = 0
            expired_count = 0
            
            for key, entry in self._cache.items():
                if datetime.now() > entry["expires_at"]:
                    expired_count += 1
                else:
                    valid_count += 1
            
            return {
                "total_entries": len(self._cache),
                "valid_entries": valid_count,
                "expired_entries": expired_count,
                "max_size": self._max_size
            }


# 全局缓存实例
rag_cache = SimpleCache(max_size=500, default_ttl=300)
user_cache = SimpleCache(max_size=100, default_ttl=600)


def cached(cache_instance: SimpleCache, ttl: Optional[int] = None):
    """
    缓存装饰器
    
    Args:
        cache_instance: 缓存实例
        ttl: 过期时间
        
    Returns:
        装饰后的函数
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = cache_instance._generate_key(func.__name__, *args, **kwargs)
            
            # 尝试从缓存获取
            cached_value = cache_instance.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            cache_instance.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator


def get_cache_stats() -> dict:
    """
    获取所有缓存的统计信息
    
    Returns:
        缓存统计信息
    """
    return {
        "rag_cache": rag_cache.get_stats(),
        "user_cache": user_cache.get_stats()
    }