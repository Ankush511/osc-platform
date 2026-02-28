#!/bin/bash
# Database migration script

set -e

echo "Running database migrations..."

cd /app/backend

# Wait for database to be ready
echo "Waiting for database to be ready..."
until PGPASSWORD="${POSTGRES_PASSWORD}" psql -h "${DB_HOST:-postgres}" -U "${POSTGRES_USER:-postgres}" -d "${POSTGRES_DB:-oscp_db}" -c '\q' 2>/dev/null; do
    echo "Database is unavailable - sleeping"
    sleep 2
done

echo "Database is ready!"

# Run migrations
alembic upgrade head

if [ $? -eq 0 ]; then
    echo "Migrations completed successfully"
else
    echo "Migration failed!" >&2
    exit 1
fi
