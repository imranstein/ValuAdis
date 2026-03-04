"""
Performance Monitoring and Optimization

Provides performance monitoring, caching, and optimization utilities
for the ValuAdis application.
"""

import time
import functools
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
import redis
import json

from app.core.config import settings
from app.core.sentry import get_sentry_manager

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Monitor and track application performance"""
    
    def __init__(self):
        self.metrics = {}
        self.sentry_manager = get_sentry_manager()
    
    def track_execution_time(self, operation_name: str):
        """Decorator to track execution time of functions"""
        def decorator(func: Callable):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    
                    # Record metric
                    self.record_metric(f"{operation_name}_duration", execution_time)
                    
                    # Log slow operations
                    if execution_time > 1.0:  # Operations taking more than 1 second
                        logger.warning(f"Slow operation: {operation_name} took {execution_time:.2f}s")
                        self.sentry_manager.add_breadcrumb(
                            category="performance",
                            message=f"Slow operation: {operation_name}",
                            level="warning",
                            data={"duration": execution_time}
                        )
                    
                    return result
                    
                except Exception as e:
                    execution_time = time.time() - start_time
                    self.sentry_manager.add_breadcrumb(
                        category="performance",
                        message=f"Failed operation: {operation_name}",
                        level="error",
                        data={"duration": execution_time, "error": str(e)}
                    )
                    raise
                    
            return wrapper
        return decorator
    
    def record_metric(self, metric_name: str, value: float, tags: Optional[Dict] = None):
        """Record a performance metric"""
        timestamp = datetime.utcnow().isoformat()
        
        if metric_name not in self.metrics:
            self.metrics[metric_name] = []
        
        self.metrics[metric_name].append({
            "value": value,
            "timestamp": timestamp,
            "tags": tags or {}
        })
        
        # Keep only last 1000 metrics per name
        if len(self.metrics[metric_name]) > 1000:
            self.metrics[metric_name] = self.metrics[metric_name][-1000:]
    
    def get_metric_summary(self, metric_name: str, minutes: int = 60) -> Dict[str, float]:
        """Get summary statistics for a metric"""
        if metric_name not in self.metrics:
            return {}
        
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        recent_metrics = [
            m for m in self.metrics[metric_name]
            if datetime.fromisoformat(m["timestamp"]) > cutoff_time
        ]
        
        if not recent_metrics:
            return {}
        
        values = [m["value"] for m in recent_metrics]
        return {
            "count": len(values),
            "avg": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
            "latest": values[-1]
        }
    
    def get_all_metrics_summary(self) -> Dict[str, Dict[str, float]]:
        """Get summary of all metrics"""
        summary = {}
        for metric_name in self.metrics:
            summary[metric_name] = self.get_metric_summary(metric_name)
        return summary


class CacheManager:
    """Redis-based caching manager"""
    
    def __init__(self):
        self.redis_client = None
        self.default_ttl = 3600  # 1 hour
        self._initialize_redis()
    
    def _initialize_redis(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            # Test connection
            self.redis_client.ping()
            logger.info("Redis cache initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Redis cache: {e}")
            self.redis_client = None
    
    def is_available(self) -> bool:
        """Check if Redis cache is available"""
        if not self.redis_client:
            return False
        
        try:
            self.redis_client.ping()
            return True
        except:
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.is_available():
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        if not self.is_available():
            return False
        
        try:
            ttl = ttl or self.default_ttl
            serialized_value = json.dumps(value, default=str)
            return self.redis_client.setex(key, ttl, serialized_value)
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.is_available():
            return False
        
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear keys matching pattern"""
        if not self.is_available():
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache clear pattern error for {pattern}: {e}")
            return 0
    
    def cache_decorator(self, key_prefix: str, ttl: Optional[int] = None):
        """Decorator for caching function results"""
        def decorator(func: Callable):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = f"{key_prefix}:{hash(str(args) + str(sorted(kwargs.items())))}"
                
                # Try to get from cache
                cached_result = self.get(cache_key)
                if cached_result is not None:
                    return cached_result
                
                # Execute function and cache result
                result = func(*args, **kwargs)
                self.set(cache_key, result, ttl)
                return result
                
            return wrapper
        return decorator


class DatabaseOptimizer:
    """Database performance optimization utilities"""
    
    @staticmethod
    def optimize_query(query, limit: int = 1000, timeout: int = 30):
        """Add performance optimizations to database queries"""
        # Add limit if not present
        if "LIMIT" not in query.upper():
            query += f" LIMIT {limit}"
        
        # Add timeout
        query += f" /*+ MAX_EXECUTION_TIME({timeout}) */"
        
        return query
    
    @staticmethod
    def get_slow_query_threshold() -> int:
        """Get threshold for slow queries in milliseconds"""
        return int(os.getenv("SLOW_QUERY_THRESHOLD", "1000"))


class ResourceMonitor:
    """Monitor system resources"""
    
    def __init__(self):
        self.sentry_manager = get_sentry_manager()
    
    def check_memory_usage(self) -> Dict[str, float]:
        """Check current memory usage"""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            
            memory_mb = memory_info.rss / 1024 / 1024
            memory_percent = process.memory_percent()
            
            # Alert if memory usage is high
            if memory_percent > 80:
                self.sentry_manager.capture_message(
                    f"High memory usage: {memory_percent:.1f}%",
                    level="warning",
                    extra_data={"memory_mb": memory_mb, "memory_percent": memory_percent}
                )
            
            return {
                "memory_mb": memory_mb,
                "memory_percent": memory_percent
            }
        except ImportError:
            logger.warning("psutil not available for memory monitoring")
            return {}
        except Exception as e:
            logger.error(f"Error checking memory usage: {e}")
            return {}
    
    def check_disk_usage(self, path: str = "/") -> Dict[str, float]:
        """Check disk usage"""
        try:
            import psutil
            disk_usage = psutil.disk_usage(path)
            
            used_percent = (disk_usage.used / disk_usage.total) * 100
            
            # Alert if disk usage is high
            if used_percent > 85:
                self.sentry_manager.capture_message(
                    f"High disk usage: {used_percent:.1f}%",
                    level="warning",
                    extra_data={"path": path, "used_percent": used_percent}
                )
            
            return {
                "total_gb": disk_usage.total / 1024 / 1024 / 1024,
                "used_gb": disk_usage.used / 1024 / 1024 / 1024,
                "free_gb": disk_usage.free / 1024 / 1024 / 1024,
                "used_percent": used_percent
            }
        except ImportError:
            logger.warning("psutil not available for disk monitoring")
            return {}
        except Exception as e:
            logger.error(f"Error checking disk usage: {e}")
            return {}


# Global instances
performance_monitor = PerformanceMonitor()
cache_manager = CacheManager()
resource_monitor = ResourceMonitor()


# Decorators for easy use
def track_performance(operation_name: str):
    """Track performance of a function"""
    return performance_monitor.track_execution_time(operation_name)


def cache_result(key_prefix: str, ttl: Optional[int] = None):
    """Cache function results"""
    return cache_manager.cache_decorator(key_prefix, ttl)


# Utility functions
def get_performance_metrics() -> Dict[str, Dict[str, float]]:
    """Get all performance metrics"""
    return performance_monitor.get_all_metrics_summary()


def clear_cache_pattern(pattern: str) -> int:
    """Clear cache keys matching pattern"""
    return cache_manager.clear_pattern(pattern)


def check_system_resources() -> Dict[str, Any]:
    """Check system resource usage"""
    return {
        "memory": resource_monitor.check_memory_usage(),
        "disk": resource_monitor.check_disk_usage(),
        "cache_available": cache_manager.is_available()
    }
