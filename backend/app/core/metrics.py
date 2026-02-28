"""
Prometheus metrics for monitoring application performance.
"""
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request, Response
from typing import Callable
import time

# Request metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

http_requests_in_progress = Gauge(
    'http_requests_in_progress',
    'Number of HTTP requests in progress',
    ['method', 'endpoint']
)

# Database metrics
db_pool_connections_in_use = Gauge(
    'db_pool_connections_in_use',
    'Number of database connections currently in use'
)

db_pool_connections_max = Gauge(
    'db_pool_connections_max',
    'Maximum number of database connections'
)

db_query_duration_seconds = Histogram(
    'db_query_duration_seconds',
    'Database query duration in seconds',
    ['query_type']
)

# Redis metrics
redis_operations_total = Counter(
    'redis_operations_total',
    'Total Redis operations',
    ['operation', 'status']
)

redis_operation_duration_seconds = Histogram(
    'redis_operation_duration_seconds',
    'Redis operation duration in seconds',
    ['operation']
)

# Business metrics
github_api_calls_total = Counter(
    'github_api_calls_total',
    'Total GitHub API calls',
    ['endpoint', 'status']
)

ai_api_calls_total = Counter(
    'ai_api_calls_total',
    'Total AI API calls',
    ['model', 'status']
)

issues_claimed_total = Counter(
    'issues_claimed_total',
    'Total issues claimed by users'
)

issues_completed_total = Counter(
    'issues_completed_total',
    'Total issues completed'
)

prs_submitted_total = Counter(
    'prs_submitted_total',
    'Total pull requests submitted'
)

prs_merged_total = Counter(
    'prs_merged_total',
    'Total pull requests merged'
)

active_users = Gauge(
    'active_users',
    'Number of active users'
)

# Celery metrics
celery_tasks_total = Counter(
    'celery_tasks_total',
    'Total Celery tasks',
    ['task_name', 'status']
)

celery_task_duration_seconds = Histogram(
    'celery_task_duration_seconds',
    'Celery task duration in seconds',
    ['task_name']
)

celery_queue_length = Gauge(
    'celery_queue_length',
    'Number of tasks in Celery queue',
    ['queue_name']
)


async def metrics_middleware(request: Request, call_next: Callable) -> Response:
    """
    Middleware to track request metrics.
    """
    method = request.method
    endpoint = request.url.path
    
    # Skip metrics endpoint itself
    if endpoint == "/metrics":
        return await call_next(request)
    
    # Track in-progress requests
    http_requests_in_progress.labels(method=method, endpoint=endpoint).inc()
    
    # Track request duration
    start_time = time.time()
    
    try:
        response = await call_next(request)
        status = response.status_code
    except Exception as e:
        status = 500
        raise
    finally:
        duration = time.time() - start_time
        
        # Record metrics
        http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status=status
        ).inc()
        
        http_request_duration_seconds.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
        
        http_requests_in_progress.labels(
            method=method,
            endpoint=endpoint
        ).dec()
    
    return response


async def metrics_endpoint() -> Response:
    """
    Endpoint to expose Prometheus metrics.
    """
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
