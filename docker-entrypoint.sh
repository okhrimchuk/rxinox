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

# Run migrations only (catalog loading and image downloading moved to background jobs)
echo "Running migrations..."
python manage.py migrate --noinput

# Background jobs (catalog loading, image downloading) will run automatically
# after the server starts via Django's AppConfig.ready() method

# Execute command
exec "$@"

