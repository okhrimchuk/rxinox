# Background Jobs System

> **⚠️ Disclaimer:** This project was developed using Cursor AI with zero manual coding and is an experimental project. The background job system may not work as expected, may contain bugs, and has not been thoroughly tested. Use at your own risk.

## Overview

To improve startup time on Render.com and other hosting platforms, heavy operations (catalog loading, image downloading) have been moved to background jobs that run **after** the server has started. This allows the application to respond to requests immediately while background tasks complete.

## How It Works

### Startup Flow

1. **Fast Startup**: Server starts with only essential operations:
   - Database migrations
   - Static files collection
   - Gunicorn server startup

2. **Background Jobs**: After server starts (15 seconds delay), background jobs run automatically:
   - Catalog loading (if `catalog-2025.csv` exists and hasn't been loaded)
   - Category image downloading

### Implementation

The background job system is implemented in `pages/apps.py` using Django's `AppConfig.ready()` method:

- Background jobs run in a **separate daemon thread**
- Jobs start **15 seconds after server startup** (allows server to be ready)
- Jobs run **only once** per application instance
- Can be disabled with `DISABLE_BACKGROUND_JOBS=true` environment variable

## Startup Scripts

### Render.com (`render-start.sh`)

Minimal startup script that:
1. Waits for database connection
2. Collects static files
3. Runs migrations
4. Starts Gunicorn server

Background jobs run automatically via `PagesConfig.ready()`.

### Docker (`docker-entrypoint.sh`)

Updated to remove catalog loading from startup:
1. Waits for database
2. Collects static files
3. Runs migrations
4. Executes the command (runs server)

Background jobs run automatically after server starts.

## Manual Background Jobs

You can also run background jobs manually:

```bash
# Run all background jobs
python manage.py run_background_jobs --all

# Run specific jobs
python manage.py run_background_jobs --load-catalog
python manage.py run_background_jobs --download-images

# Wait for database before running
python manage.py run_background_jobs --all --wait-for-db 10
```

## Configuration

### Environment Variables

- `DISABLE_BACKGROUND_JOBS=true`: Disable automatic background jobs
- `DATABASE_URL`: Database connection (automatically detected on Render)

### File Flags

- `db_loaded.flag`: Created after catalog is loaded, prevents reloading on restart

## Background Jobs Details

### Catalog Loading

- **Trigger**: Runs if `catalog-2025.csv` exists and `db_loaded.flag` doesn't exist
- **Command**: `load_catalog`
- **Status**: Creates `db_loaded.flag` after successful load

### Image Downloading

- **Trigger**: Always runs after catalog is loaded
- **Command**: `download_category_images`
- **Notes**: Downloads images for categories that don't have local images yet

## Troubleshooting

### Background Jobs Not Running

1. Check if `DISABLE_BACKGROUND_JOBS` is set to `true`
2. Check application logs for background job errors
3. Verify server is running (background jobs only run when server is active)
4. Check if jobs were already run (flag files exist)

### Jobs Running Multiple Times

- Background jobs use a class-level flag to prevent multiple runs
- If you see multiple runs, check if multiple server processes are starting

### Long Startup Time

- Background jobs should **not** block startup (they run in separate thread)
- If startup is still slow, check:
  - Database connection time
  - Static files collection time
  - Migration time

## Disabling Background Jobs

To disable automatic background jobs (e.g., for testing):

```bash
# Set environment variable
export DISABLE_BACKGROUND_JOBS=true

# Or in .env file
DISABLE_BACKGROUND_JOBS=true
```

Then run jobs manually when needed:
```bash
python manage.py run_background_jobs --all
```

## Future Improvements

Potential enhancements:
- Use Django-Q or Celery for more robust background job processing
- Add job status tracking
- Add job scheduling (cron-like)
- Add job retry logic
- Add job progress reporting

## Notes

- Background jobs run in **daemon threads** (will stop when main process stops)
- Jobs are **fire-and-forget** (no status tracking)
- Jobs run **once per application instance** (not per request)
- Jobs are **best-effort** (failures are logged but don't crash the server)
