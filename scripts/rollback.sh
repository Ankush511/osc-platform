#!/bin/bash
# Rollback script for production deployment

set -e

echo "========================================="
echo "OSCP Production Rollback"
echo "========================================="

COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env.production"

# Load environment variables
if [ -f "${ENV_FILE}" ]; then
    export $(cat ${ENV_FILE} | grep -v '^#' | xargs)
fi

# Confirm rollback
echo "WARNING: This will rollback to the previous version!"
read -p "Are you sure you want to rollback? (yes/no): " CONFIRM
if [ "${CONFIRM}" != "yes" ]; then
    echo "Rollback cancelled."
    exit 0
fi

echo ""
echo "Step 1: Checking out previous version..."
CURRENT_COMMIT=$(git rev-parse HEAD)
PREVIOUS_COMMIT=$(git rev-parse HEAD~1)

echo "Current commit: ${CURRENT_COMMIT}"
echo "Rolling back to: ${PREVIOUS_COMMIT}"

git checkout ${PREVIOUS_COMMIT}

echo ""
echo "Step 2: Stopping current services..."
docker-compose -f ${COMPOSE_FILE} down

echo ""
echo "Step 3: Rebuilding images with previous version..."
docker-compose -f ${COMPOSE_FILE} build --no-cache

echo ""
echo "Step 4: Starting services..."
docker-compose -f ${COMPOSE_FILE} up -d

echo ""
echo "Step 5: Checking database migration status..."
docker-compose -f ${COMPOSE_FILE} run --rm backend alembic current

echo ""
read -p "Do you need to rollback database migrations? (yes/no): " ROLLBACK_DB
if [ "${ROLLBACK_DB}" == "yes" ]; then
    read -p "Enter the migration revision to rollback to: " REVISION
    docker-compose -f ${COMPOSE_FILE} run --rm backend alembic downgrade ${REVISION}
fi

echo ""
echo "========================================="
echo "Rollback completed!"
echo "========================================="
echo ""
echo "Current version: ${PREVIOUS_COMMIT}"
echo ""
echo "To return to the latest version, run:"
echo "  git checkout main"
echo "  ./scripts/deploy.sh"
