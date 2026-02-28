#!/bin/bash
# Health check script for production services

set -e

echo "========================================="
echo "OSCP Health Check"
echo "========================================="

COMPOSE_FILE="docker-compose.prod.yml"
BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:3000}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_service() {
    local service_name=$1
    local url=$2
    
    echo -n "Checking ${service_name}... "
    
    if curl -f -s -o /dev/null -w "%{http_code}" "${url}" | grep -q "200\|301\|302"; then
        echo -e "${GREEN}✓ OK${NC}"
        return 0
    else
        echo -e "${RED}✗ FAILED${NC}"
        return 1
    fi
}

check_container() {
    local container_name=$1
    
    echo -n "Checking container ${container_name}... "
    
    if docker ps --filter "name=${container_name}" --filter "status=running" | grep -q "${container_name}"; then
        echo -e "${GREEN}✓ Running${NC}"
        return 0
    else
        echo -e "${RED}✗ Not Running${NC}"
        return 1
    fi
}

# Check Docker containers
echo ""
echo "Container Status:"
check_container "oscp_postgres_prod"
check_container "oscp_redis_prod"
check_container "oscp_backend_prod"
check_container "oscp_celery_worker_prod"
check_container "oscp_celery_beat_prod"
check_container "oscp_frontend_prod"
check_container "oscp_nginx_prod"

# Check service endpoints
echo ""
echo "Service Endpoints:"
check_service "Backend API" "${BACKEND_URL}/health"
check_service "Frontend" "${FRONTEND_URL}"

# Check database connection
echo ""
echo -n "Checking database connection... "
if docker exec oscp_postgres_prod pg_isready -U postgres > /dev/null 2>&1; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
fi

# Check Redis connection
echo -n "Checking Redis connection... "
if docker exec oscp_redis_prod redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
fi

# Check disk space
echo ""
echo "Disk Usage:"
df -h | grep -E "Filesystem|/$"

# Check memory usage
echo ""
echo "Memory Usage:"
free -h

# Check Docker stats
echo ""
echo "Container Resource Usage:"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" \
    oscp_postgres_prod oscp_redis_prod oscp_backend_prod oscp_frontend_prod 2>/dev/null || echo "Unable to get stats"

echo ""
echo "========================================="
echo "Health Check Complete"
echo "========================================="
