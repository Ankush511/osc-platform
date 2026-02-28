#!/bin/bash
# Production deployment script

set -e

echo "========================================="
echo "OSCP Production Deployment"
echo "========================================="

# Configuration
ENVIRONMENT="${ENVIRONMENT:-production}"
COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env.production"

# Check if environment file exists
if [ ! -f "${ENV_FILE}" ]; then
    echo "Error: ${ENV_FILE} not found!"
    echo "Please copy .env.production.example to ${ENV_FILE} and configure it."
    exit 1
fi

# Load environment variables
export $(cat ${ENV_FILE} | grep -v '^#' | xargs)

echo "Environment: ${ENVIRONMENT}"
echo ""

# Confirm deployment
read -p "Are you sure you want to deploy to production? (yes/no): " CONFIRM
if [ "${CONFIRM}" != "yes" ]; then
    echo "Deployment cancelled."
    exit 0
fi

echo ""
echo "Step 1: Pulling latest code..."
git pull origin main

echo ""
echo "Step 2: Building Docker images..."
docker-compose -f ${COMPOSE_FILE} build --no-cache

echo ""
echo "Step 3: Stopping existing containers..."
docker-compose -f ${COMPOSE_FILE} down

echo ""
echo "Step 4: Starting database and Redis..."
docker-compose -f ${COMPOSE_FILE} up -d postgres redis

echo "Waiting for database to be ready..."
sleep 10

echo ""
echo "Step 5: Running database migrations..."
docker-compose -f ${COMPOSE_FILE} run --rm backend alembic upgrade head

echo ""
echo "Step 6: Starting all services..."
docker-compose -f ${COMPOSE_FILE} up -d

echo ""
echo "Step 7: Waiting for services to be healthy..."
sleep 15

# Check service health
echo ""
echo "Checking service health..."
docker-compose -f ${COMPOSE_FILE} ps

echo ""
echo "========================================="
echo "Deployment completed successfully!"
echo "========================================="
echo ""
echo "Services:"
echo "  - Frontend: http://localhost:3000"
echo "  - Backend API: http://localhost:8000"
echo "  - Grafana: http://localhost:3001"
echo "  - Prometheus: http://localhost:9090"
echo ""
echo "To view logs: docker-compose -f ${COMPOSE_FILE} logs -f"
echo "To stop services: docker-compose -f ${COMPOSE_FILE} down"
