"""
Performance monitoring utilities for tracking API response times and database queries.
"""
import time
import logging
from functools import wraps
from typing import Callable, Any
from contextlib import contextmanager

logger = logging.getLogger(__name__)


def measure_time(func: Callable) -> Callable:
    """
    Decorator to measure function execution time.
    
    Usage:
        @measure_time
        def my_function():
            pass
    """
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            duration = time.time() - start_time
            logger.info(f"{func.__name__} took {duration:.3f}s")
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            duration = time.time() - start_time
            logger.info(f"{func.__name__} took {duration:.3f}s")
    
    # Return appropriate wrapper based on function type
    import asyncio
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper


@contextmanager
def timer(operation_name: str):
    """
    Context manager for timing code blocks.
    
    Usage:
        with timer("database query"):
            db.query(User).all()
    """
    start_time = time.time()
    try:
        yield
    finally:
        duration = time.time() - start_time
        logger.info(f"{operation_name} took {duration:.3f}s")


class PerformanceMonitor:
    """
    Performance monitoring class for tracking metrics.
    """
    
    def __init__(self):
        self.metrics = {}
    
    def record_metric(self, name: str, value: float, unit: str = "ms"):
        """
        Record a performance metric.
        
        Args:
            name: Metric name
            value: Metric value
            unit: Unit of measurement
        """
        if name not in self.metrics:
            self.metrics[name] = []
        
        self.metrics[name].append({
            "value": value,
            "unit": unit,
            "timestamp": time.time()
        })
    
    def get_average(self, name: str) -> float:
        """
        Get average value for a metric.
        
        Args:
            name: Metric name
            
        Returns:
            Average value or 0 if no data
        """
        if name not in self.metrics or not self.metrics[name]:
            return 0.0
        
        values = [m["value"] for m in self.metrics[name]]
        return sum(values) / len(values)
    
    def get_percentile(self, name: str, percentile: int = 95) -> float:
        """
        Get percentile value for a metric.
        
        Args:
            name: Metric name
            percentile: Percentile to calculate (0-100)
            
        Returns:
            Percentile value or 0 if no data
        """
        if name not in self.metrics or not self.metrics[name]:
            return 0.0
        
        values = sorted([m["value"] for m in self.metrics[name]])
        index = int(len(values) * percentile / 100)
        return values[min(index, len(values) - 1)]
    
    def clear_metrics(self, name: str = None):
        """
        Clear metrics.
        
        Args:
            name: Metric name to clear, or None to clear all
        """
        if name:
            self.metrics.pop(name, None)
        else:
            self.metrics.clear()
    
    def get_summary(self) -> dict:
        """
        Get summary of all metrics.
        
        Returns:
            Dictionary with metric summaries
        """
        summary = {}
        for name in self.metrics:
            summary[name] = {
                "count": len(self.metrics[name]),
                "average": self.get_average(name),
                "p95": self.get_percentile(name, 95),
                "p99": self.get_percentile(name, 99),
            }
        return summary


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


def log_slow_queries(threshold_ms: float = 100):
    """
    Decorator to log slow database queries.
    
    Args:
        threshold_ms: Threshold in milliseconds for logging
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            duration_ms = (time.time() - start_time) * 1000
            
            if duration_ms > threshold_ms:
                logger.warning(
                    f"Slow query detected: {func.__name__} took {duration_ms:.2f}ms "
                    f"(threshold: {threshold_ms}ms)"
                )
            
            performance_monitor.record_metric(f"query_{func.__name__}", duration_ms, "ms")
            return result
        
        return wrapper
    return decorator
