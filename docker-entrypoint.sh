#!/bin/bash
set -e

# Wait for database if using PostgreSQL
if [ "$DATABASE" = "postgres" ] || [ -n "$POSTGRES_DB" ]; then
    echo "Waiting for database..."
    python wait_for_db.py || echo "Database wait skipped, continuing..."
fi

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput || true

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Load catalog data if file exists and database is empty
if [ -f "catalog-2025.csv" ] && [ ! -f "db_loaded.flag" ]; then
    echo "Loading catalog data..."
    python manage.py load_catalog || true
    touch db_loaded.flag
fi

# Execute command
exec "$@"

