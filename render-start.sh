#!/bin/bash
# Startup script for Render.com deployment
# This script does minimal work to start the server quickly
# Background jobs (catalog loading, image downloading) run after server starts

# Don't use set -e to allow graceful handling of errors
# We'll handle errors explicitly for each command

echo "=== Render Startup Script ==="

# Wait for database connection (non-fatal)
echo "Waiting for database..."
python wait_for_db.py || echo "Database wait skipped, continuing..."

# Collect static files (optional - WhiteNoise can serve from STATICFILES_DIRS directly)
# Run collectstatic in background after server starts for faster startup
echo "Skipping static files collection (will run in background)..."
# Background job will handle collectstatic if needed

# Disable background jobs during migrations to prevent interference
export DISABLE_BACKGROUND_JOBS=true

# Run migrations only (fast)
echo "Running migrations..."
python manage.py migrate --noinput || echo "Migrations had issues, continuing..."

# Re-enable background jobs for server runtime
export DISABLE_BACKGROUND_JOBS=false

# Start the server (this should not return)
# Background jobs will run automatically after server starts
echo "Starting Gunicorn server..."

# Render provides PORT environment variable automatically
# If PORT is not set, use default 8000
PORT=${PORT:-8000}
exec gunicorn rxinox.wsgi:application --bind 0.0.0.0:$PORT

