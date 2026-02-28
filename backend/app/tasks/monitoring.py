"""
Task monitoring and error handling utilities

Provides monitoring, logging, and error handling for background tasks.
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from app.celery_app import celery_app
from app.db.base import SessionLocal

logger = logging.getLogger(__name__)


class TaskMonitor:
    """
    Monitor for tracking task execution and health.
    
    Provides utilities for:
    - Task execution tracking
    - Error rate monitoring
    - Performance metrics
    - Health checks
    """
    
    def __init__(self):
        self.task_stats = {}
    
    def record_task_execution(
        self,
        task_name: str,
        success: bool,
        duration_seconds: float,
        error: Optional[str] = None
    ):
        """
        Record task execution statistics.
        
        Args:
            task_name: Name of the task
            success: Whether task succeeded
            duration_seconds: Task execution duration
            error: Error message if failed
        """
        if task_name not in self.task_stats:
            self.task_stats[task_name] = {
                "total_runs": 0,
                "successful_runs": 0,
                "failed_runs": 0,
                "total_duration": 0.0,
                "last_run": None,
                "last_error": None
            }
        
        stats = self.task_stats[task_name]
        stats["total_runs"] += 1
        stats["total_duration"] += duration_seconds
        stats["last_run"] = datetime.utcnow()
        
        if success:
            stats["successful_runs"] += 1
        else:
            stats["failed_runs"] += 1
            stats["last_error"] = error
    
    def get_task_stats(self, task_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get task execution statistics.
        
        Args:
            task_name: Optional specific task name, or None for all tasks
            
        Returns:
            Dictionary of task statistics
        """
        if task_name:
            return self.task_stats.get(task_name, {})
        return self.task_stats
    
    def get_error_rate(self, task_name: str) -> float:
        """
        Calculate error rate for a task.
        
        Args:
            task_name: Name of the task
            
        Returns:
            Error rate as a percentage (0-100)
        """
        stats = self.task_stats.get(task_name)
        if not stats or stats["total_runs"] == 0:
            return 0.0
        
        return (stats["failed_runs"] / stats["total_runs"]) * 100
    
    def get_average_duration(self, task_name: str) -> float:
        """
        Calculate average execution duration for a task.
        
        Args:
            task_name: Name of the task
            
        Returns:
            Average duration in seconds
        """
        stats = self.task_stats.get(task_name)
        if not stats or stats["total_runs"] == 0:
            return 0.0
        
        return stats["total_duration"] / stats["total_runs"]


# Global task monitor instance
task_monitor = TaskMonitor()


@celery_app.task(name="app.tasks.monitoring.health_check_task")
def health_check_task():
    """
    Perform health check on the background job system.
    
    Checks:
    - Database connectivity
    - Redis connectivity
    - Task queue status
    - Recent task failures
    
    Returns health status and metrics.
    """
    logger.info("Running background job health check")
    
    health_status = {
        "timestamp": datetime.utcnow().isoformat(),
        "status": "healthy",
        "checks": {},
        "metrics": {}
    }
    
    # Check database connectivity
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        health_status["checks"]["database"] = "ok"
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        health_status["checks"]["database"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Check Redis connectivity
    try:
        from redis import Redis
        from app.core.config import settings
        redis_client = Redis.from_url(settings.REDIS_URL)
        redis_client.ping()
        health_status["checks"]["redis"] = "ok"
    except Exception as e:
        logger.error(f"Redis health check failed: {str(e)}")
        health_status["checks"]["redis"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Check Celery worker status
    try:
        inspect = celery_app.control.inspect()
        active_workers = inspect.active()
        
        if active_workers:
            health_status["checks"]["celery_workers"] = "ok"
            health_status["metrics"]["active_workers"] = len(active_workers)
        else:
            health_status["checks"]["celery_workers"] = "no active workers"
            health_status["status"] = "degraded"
    except Exception as e:
        logger.error(f"Celery worker check failed: {str(e)}")
        health_status["checks"]["celery_workers"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Add task statistics
    health_status["metrics"]["task_stats"] = task_monitor.get_task_stats()
    
    logger.info(f"Health check completed: {health_status['status']}")
    return health_status


@celery_app.task(name="app.tasks.monitoring.cleanup_old_task_results")
def cleanup_old_task_results(days: int = 7):
    """
    Clean up old task results from Redis.
    
    Args:
        days: Number of days to keep results (default 7)
    
    This helps prevent Redis from growing indefinitely with old task results.
    """
    logger.info(f"Cleaning up task results older than {days} days")
    
    try:
        from redis import Redis
        from app.core.config import settings
        
        redis_client = Redis.from_url(settings.REDIS_URL)
        
        # Get all celery result keys
        pattern = "celery-task-meta-*"
        keys = redis_client.keys(pattern)
        
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        deleted_count = 0
        
        for key in keys:
            try:
                # Check if key has TTL set
                ttl = redis_client.ttl(key)
                
                # If no TTL or very long TTL, check age
                if ttl == -1 or ttl > days * 86400:
                    # Get the result to check timestamp
                    result = redis_client.get(key)
                    if result:
                        # If we can't determine age, set a reasonable TTL
                        redis_client.expire(key, days * 86400)
                        deleted_count += 1
            except Exception as e:
                logger.warning(f"Error processing key {key}: {str(e)}")
                continue
        
        logger.info(f"Cleanup completed: processed {len(keys)} keys, set TTL on {deleted_count}")
        
        return {
            "success": True,
            "total_keys": len(keys),
            "processed": deleted_count
        }
        
    except Exception as e:
        logger.error(f"Cleanup task failed: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


@celery_app.task(name="app.tasks.monitoring.generate_task_report")
def generate_task_report():
    """
    Generate a comprehensive report of task execution statistics.
    
    Returns detailed metrics about all background tasks including:
    - Execution counts
    - Success/failure rates
    - Average durations
    - Recent errors
    """
    logger.info("Generating task execution report")
    
    report = {
        "generated_at": datetime.utcnow().isoformat(),
        "tasks": {}
    }
    
    # Get statistics for all tasks
    all_stats = task_monitor.get_task_stats()
    
    for task_name, stats in all_stats.items():
        report["tasks"][task_name] = {
            "total_runs": stats["total_runs"],
            "successful_runs": stats["successful_runs"],
            "failed_runs": stats["failed_runs"],
            "success_rate": (
                (stats["successful_runs"] / stats["total_runs"] * 100)
                if stats["total_runs"] > 0 else 0
            ),
            "error_rate": task_monitor.get_error_rate(task_name),
            "average_duration": task_monitor.get_average_duration(task_name),
            "last_run": stats["last_run"].isoformat() if stats["last_run"] else None,
            "last_error": stats["last_error"]
        }
    
    # Get Celery queue statistics
    try:
        inspect = celery_app.control.inspect()
        
        # Get scheduled tasks
        scheduled = inspect.scheduled()
        if scheduled:
            report["scheduled_tasks"] = {
                worker: len(tasks) for worker, tasks in scheduled.items()
            }
        
        # Get active tasks
        active = inspect.active()
        if active:
            report["active_tasks"] = {
                worker: len(tasks) for worker, tasks in active.items()
            }
        
        # Get reserved tasks
        reserved = inspect.reserved()
        if reserved:
            report["reserved_tasks"] = {
                worker: len(tasks) for worker, tasks in reserved.items()
            }
    except Exception as e:
        logger.error(f"Failed to get Celery statistics: {str(e)}")
        report["celery_stats_error"] = str(e)
    
    logger.info("Task report generated successfully")
    return report


def handle_task_error(task_name: str, error: Exception, context: Dict[str, Any]):
    """
    Centralized error handling for tasks.
    
    Args:
        task_name: Name of the task that failed
        error: The exception that occurred
        context: Additional context about the error
    """
    logger.error(
        f"Task {task_name} failed: {str(error)}",
        extra={
            "task_name": task_name,
            "error_type": type(error).__name__,
            "context": context
        },
        exc_info=True
    )
    
    # Record in monitor
    task_monitor.record_task_execution(
        task_name=task_name,
        success=False,
        duration_seconds=context.get("duration", 0),
        error=str(error)
    )
    
    # TODO: Send alert if error rate exceeds threshold
    error_rate = task_monitor.get_error_rate(task_name)
    if error_rate > 50:  # More than 50% failure rate
        logger.critical(
            f"High error rate detected for task {task_name}: {error_rate:.1f}%"
        )


def handle_task_success(task_name: str, duration_seconds: float, result: Any):
    """
    Handle successful task completion.
    
    Args:
        task_name: Name of the task
        duration_seconds: Task execution duration
        result: Task result
    """
    logger.info(
        f"Task {task_name} completed successfully in {duration_seconds:.2f}s"
    )
    
    # Record in monitor
    task_monitor.record_task_execution(
        task_name=task_name,
        success=True,
        duration_seconds=duration_seconds
    )
