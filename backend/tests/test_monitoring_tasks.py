"""
Tests for task monitoring and health check functionality
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from app.tasks.monitoring import (
    TaskMonitor,
    task_monitor,
    health_check_task,
    cleanup_old_task_results,
    generate_task_report,
    handle_task_error,
    handle_task_success
)


class TestTaskMonitor:
    """Tests for TaskMonitor class"""
    
    def test_task_monitor_initialization(self):
        """Test task monitor initializes correctly"""
        monitor = TaskMonitor()
        assert monitor.task_stats == {}
    
    def test_record_task_execution_success(self):
        """Test recording successful task execution"""
        monitor = TaskMonitor()
        
        monitor.record_task_execution(
            task_name="test_task",
            success=True,
            duration_seconds=5.5
        )
        
        stats = monitor.get_task_stats("test_task")
        assert stats["total_runs"] == 1
        assert stats["successful_runs"] == 1
        assert stats["failed_runs"] == 0
        assert stats["total_duration"] == 5.5
        assert stats["last_run"] is not None
    
    def test_record_task_execution_failure(self):
        """Test recording failed task execution"""
        monitor = TaskMonitor()
        
        monitor.record_task_execution(
            task_name="test_task",
            success=False,
            duration_seconds=2.0,
            error="Task failed due to timeout"
        )
        
        stats = monitor.get_task_stats("test_task")
        assert stats["total_runs"] == 1
        assert stats["successful_runs"] == 0
        assert stats["failed_runs"] == 1
        assert stats["last_error"] == "Task failed due to timeout"
    
    def test_record_multiple_executions(self):
        """Test recording multiple task executions"""
        monitor = TaskMonitor()
        
        # Record 3 successful and 2 failed executions
        for i in range(3):
            monitor.record_task_execution("test_task", True, 1.0)
        
        for i in range(2):
            monitor.record_task_execution("test_task", False, 2.0, "Error")
        
        stats = monitor.get_task_stats("test_task")
        assert stats["total_runs"] == 5
        assert stats["successful_runs"] == 3
        assert stats["failed_runs"] == 2
        assert stats["total_duration"] == 7.0  # 3*1.0 + 2*2.0
    
    def test_get_error_rate(self):
        """Test calculating error rate"""
        monitor = TaskMonitor()
        
        # 2 successful, 3 failed = 60% error rate
        for i in range(2):
            monitor.record_task_execution("test_task", True, 1.0)
        for i in range(3):
            monitor.record_task_execution("test_task", False, 1.0)
        
        error_rate = monitor.get_error_rate("test_task")
        assert error_rate == 60.0
    
    def test_get_error_rate_no_runs(self):
        """Test error rate for task with no runs"""
        monitor = TaskMonitor()
        error_rate = monitor.get_error_rate("nonexistent_task")
        assert error_rate == 0.0
    
    def test_get_average_duration(self):
        """Test calculating average duration"""
        monitor = TaskMonitor()
        
        monitor.record_task_execution("test_task", True, 5.0)
        monitor.record_task_execution("test_task", True, 3.0)
        monitor.record_task_execution("test_task", True, 4.0)
        
        avg_duration = monitor.get_average_duration("test_task")
        assert avg_duration == 4.0  # (5+3+4)/3
    
    def test_get_all_task_stats(self):
        """Test getting stats for all tasks"""
        monitor = TaskMonitor()
        
        monitor.record_task_execution("task1", True, 1.0)
        monitor.record_task_execution("task2", True, 2.0)
        monitor.record_task_execution("task3", False, 3.0, "Error")
        
        all_stats = monitor.get_task_stats()
        assert len(all_stats) == 3
        assert "task1" in all_stats
        assert "task2" in all_stats
        assert "task3" in all_stats


class TestHealthCheckTask:
    """Tests for health_check_task"""
    
    @patch('app.tasks.monitoring.SessionLocal')
    @patch('redis.Redis')
    @patch('app.tasks.monitoring.celery_app.control.inspect')
    def test_health_check_all_healthy(self, mock_inspect, mock_redis, mock_session_local):
        """Test health check when all systems are healthy"""
        # Mock database
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        
        # Mock Redis
        mock_redis_client = MagicMock()
        mock_redis.from_url.return_value = mock_redis_client
        mock_redis_client.ping.return_value = True
        
        # Mock Celery workers
        mock_inspect_instance = MagicMock()
        mock_inspect.return_value = mock_inspect_instance
        mock_inspect_instance.active.return_value = {"worker1": []}
        
        result = health_check_task()
        
        assert result["status"] == "healthy"
        assert result["checks"]["database"] == "ok"
        assert result["checks"]["redis"] == "ok"
        assert result["checks"]["celery_workers"] == "ok"
    
    @patch('app.tasks.monitoring.SessionLocal')
    def test_health_check_database_failure(self, mock_session_local):
        """Test health check when database is down"""
        # Mock database failure
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        mock_db.execute.side_effect = Exception("Database connection failed")
        
        result = health_check_task()
        
        assert result["status"] == "unhealthy"
        assert "error" in result["checks"]["database"]
    
    @patch('app.tasks.monitoring.SessionLocal')
    @patch('redis.Redis')
    def test_health_check_redis_failure(self, mock_redis, mock_session_local):
        """Test health check when Redis is down"""
        # Mock database OK
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        
        # Mock Redis failure
        mock_redis.from_url.side_effect = Exception("Redis connection failed")
        
        result = health_check_task()
        
        assert result["status"] == "unhealthy"
        assert "error" in result["checks"]["redis"]
    
    @patch('app.tasks.monitoring.SessionLocal')
    @patch('redis.Redis')
    @patch('app.tasks.monitoring.celery_app.control.inspect')
    def test_health_check_no_workers(self, mock_inspect, mock_redis, mock_session_local):
        """Test health check when no Celery workers are active"""
        # Mock database and Redis OK
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        
        mock_redis_client = MagicMock()
        mock_redis.from_url.return_value = mock_redis_client
        
        # Mock no active workers
        mock_inspect_instance = MagicMock()
        mock_inspect.return_value = mock_inspect_instance
        mock_inspect_instance.active.return_value = None
        
        result = health_check_task()
        
        assert result["status"] == "degraded"
        assert "no active workers" in result["checks"]["celery_workers"]


class TestCleanupOldTaskResults:
    """Tests for cleanup_old_task_results"""
    
    @patch('redis.Redis')
    def test_cleanup_task_results_success(self, mock_redis):
        """Test successful cleanup of old task results"""
        mock_redis_client = MagicMock()
        mock_redis.from_url.return_value = mock_redis_client
        
        # Mock keys
        mock_keys = [
            b"celery-task-meta-123",
            b"celery-task-meta-456",
            b"celery-task-meta-789"
        ]
        mock_redis_client.keys.return_value = mock_keys
        mock_redis_client.ttl.return_value = -1  # No TTL set
        mock_redis_client.get.return_value = b'{"status": "SUCCESS"}'
        
        result = cleanup_old_task_results(days=7)
        
        assert result["success"] is True
        assert result["total_keys"] == 3
        assert mock_redis_client.expire.call_count == 3
    
    @patch('redis.Redis')
    def test_cleanup_task_results_no_keys(self, mock_redis):
        """Test cleanup when there are no keys"""
        mock_redis_client = MagicMock()
        mock_redis.from_url.return_value = mock_redis_client
        mock_redis_client.keys.return_value = []
        
        result = cleanup_old_task_results(days=7)
        
        assert result["success"] is True
        assert result["total_keys"] == 0
    
    @patch('redis.Redis')
    def test_cleanup_task_results_failure(self, mock_redis):
        """Test cleanup handling Redis failure"""
        mock_redis.from_url.side_effect = Exception("Redis connection failed")
        
        result = cleanup_old_task_results(days=7)
        
        assert result["success"] is False
        assert "error" in result


class TestGenerateTaskReport:
    """Tests for generate_task_report"""
    
    @patch('app.tasks.monitoring.task_monitor')
    @patch('app.tasks.monitoring.celery_app.control.inspect')
    def test_generate_task_report_success(self, mock_inspect, mock_task_monitor):
        """Test generating task report"""
        # Mock task stats
        mock_task_monitor.get_task_stats.return_value = {
            "test_task": {
                "total_runs": 10,
                "successful_runs": 8,
                "failed_runs": 2,
                "total_duration": 50.0,
                "last_run": datetime.utcnow(),
                "last_error": None
            }
        }
        mock_task_monitor.get_error_rate.return_value = 20.0
        mock_task_monitor.get_average_duration.return_value = 5.0
        
        # Mock Celery inspect
        mock_inspect_instance = MagicMock()
        mock_inspect.return_value = mock_inspect_instance
        mock_inspect_instance.scheduled.return_value = {"worker1": []}
        mock_inspect_instance.active.return_value = {"worker1": []}
        mock_inspect_instance.reserved.return_value = {"worker1": []}
        
        result = generate_task_report()
        
        assert "generated_at" in result
        assert "tasks" in result
        assert "test_task" in result["tasks"]
        assert result["tasks"]["test_task"]["total_runs"] == 10
        assert result["tasks"]["test_task"]["success_rate"] == 80.0
    
    @patch('app.tasks.monitoring.task_monitor')
    def test_generate_task_report_no_tasks(self, mock_task_monitor):
        """Test generating report when no tasks have run"""
        mock_task_monitor.get_task_stats.return_value = {}
        
        result = generate_task_report()
        
        assert "generated_at" in result
        assert "tasks" in result
        assert len(result["tasks"]) == 0


class TestErrorHandling:
    """Tests for error handling utilities"""
    
    @patch('app.tasks.monitoring.task_monitor')
    def test_handle_task_error(self, mock_task_monitor):
        """Test handling task error"""
        # Mock get_error_rate to return a float
        mock_task_monitor.get_error_rate.return_value = 25.0
        
        error = Exception("Test error")
        context = {"duration": 5.0, "attempt": 1}
        
        handle_task_error("test_task", error, context)
        
        mock_task_monitor.record_task_execution.assert_called_once_with(
            task_name="test_task",
            success=False,
            duration_seconds=5.0,
            error="Test error"
        )
    
    @patch('app.tasks.monitoring.task_monitor')
    def test_handle_task_success(self, mock_task_monitor):
        """Test handling task success"""
        result = {"status": "completed"}
        
        handle_task_success("test_task", 3.5, result)
        
        mock_task_monitor.record_task_execution.assert_called_once_with(
            task_name="test_task",
            success=True,
            duration_seconds=3.5
        )
    
    @patch('app.tasks.monitoring.task_monitor')
    @patch('app.tasks.monitoring.logger')
    def test_handle_task_error_high_error_rate(self, mock_logger, mock_task_monitor):
        """Test handling error when error rate is high"""
        mock_task_monitor.get_error_rate.return_value = 75.0
        
        error = Exception("Test error")
        context = {"duration": 1.0}
        
        handle_task_error("test_task", error, context)
        
        # Should log critical message for high error rate
        assert mock_logger.critical.called


class TestMonitoringIntegration:
    """Integration tests for monitoring"""
    
    def test_full_monitoring_workflow(self):
        """Test complete monitoring workflow"""
        monitor = TaskMonitor()
        
        # Simulate multiple task executions
        tasks = ["sync_task", "claim_task", "pr_task"]
        
        for task in tasks:
            for i in range(5):
                success = i < 4  # 4 success, 1 failure
                monitor.record_task_execution(
                    task_name=task,
                    success=success,
                    duration_seconds=2.0 + i * 0.5,
                    error="Error" if not success else None
                )
        
        # Check statistics
        for task in tasks:
            stats = monitor.get_task_stats(task)
            assert stats["total_runs"] == 5
            assert stats["successful_runs"] == 4
            assert stats["failed_runs"] == 1
            
            error_rate = monitor.get_error_rate(task)
            assert error_rate == 20.0
            
            avg_duration = monitor.get_average_duration(task)
            assert avg_duration > 0
