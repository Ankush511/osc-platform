"""
Task monitoring utilities.
Simplified version without Celery dependency.
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class TaskMonitor:
    """Simple in-memory task execution monitor."""

    def __init__(self):
        self.task_stats = {}

    def record_task_execution(self, task_name: str, success: bool, duration_seconds: float, error: Optional[str] = None):
        if task_name not in self.task_stats:
            self.task_stats[task_name] = {
                "total_runs": 0, "successful_runs": 0, "failed_runs": 0,
                "total_duration": 0.0, "last_run": None, "last_error": None
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
        if task_name:
            return self.task_stats.get(task_name, {})
        return self.task_stats

    def get_error_rate(self, task_name: str) -> float:
        stats = self.task_stats.get(task_name)
        if not stats or stats["total_runs"] == 0:
            return 0.0
        return (stats["failed_runs"] / stats["total_runs"]) * 100


task_monitor = TaskMonitor()
