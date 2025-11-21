#!/usr/bin/env bash
# Build script for Render.com deployment

set -o errexit  # Exit on error

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Run migrations (optional - can be done after deployment)
# python manage.py migrate --noinput
