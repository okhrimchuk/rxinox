#!/bin/bash
# Startup script for Render.com deployment
# This script does minimal work to start the server quickly
# Background jobs (catalog loading, image downloading) run after server starts

set -e

echo "=== Render Startup Script ==="

# Wait for database connection
echo "Waiting for database..."
python wait_for_db.py || echo "Database wait skipped..."

# Collect static files (required before starting)
echo "Collecting static files..."
python manage.py collectstatic --noinput || true

# Run migrations only (fast)
echo "Running migrations..."
python manage.py migrate --noinput || true

# Start the server
# Background jobs will run automatically after server starts
echo "Starting Gunicorn server..."
exec gunicorn rxinox.wsgi:application

