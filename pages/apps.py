import os
import threading
from django.apps import AppConfig
from django.core.management import call_command
from django.core.management.base import CommandError


class PagesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pages'
    _background_jobs_started = False

    def ready(self):
        """Start background jobs after server is ready."""
        import sys
        
        # Skip if DISABLE_BACKGROUND_JOBS is set (e.g., during migrations)
        if os.environ.get('DISABLE_BACKGROUND_JOBS') == 'true':
            return
        
        # Prevent running multiple times
        if PagesConfig._background_jobs_started:
            return
        
        # Check if we're running a management command (skip background jobs)
        # This includes migrate, makemigrations, collectstatic, etc.
        if len(sys.argv) > 1:
            cmd = sys.argv[1]
            management_commands = [
                'migrate', 'makemigrations', 'collectstatic', 'load_catalog',
                'download_category_images', 'createsuperuser', 'shell', 'test',
                'run_background_jobs', 'check', 'flush', 'dbshell', 'dumpdata',
                'loaddata', 'diffsettings', 'inspectdb'
            ]
            if cmd in management_commands:
                return
        
        # Only run background jobs when actually running a server
        # Detection: look for runserver or if this is being called from WSGI
        # In WSGI mode, sys.argv typically won't have command arguments
        # but Django will be loaded via wsgi.py
        try:
            # Check if this is a server invocation
            is_runserver = 'runserver' in ' '.join(sys.argv) if sys.argv else False
            
            # Check if we're in WSGI context
            # WSGI apps are loaded differently - we check if we're being imported
            # by wsgi.py or if we detect WSGI environment
            import inspect
            frame = inspect.currentframe()
            wsgi_context = False
            while frame:
                filename = frame.f_code.co_filename
                if 'wsgi.py' in filename or 'asgi.py' in filename:
                    wsgi_context = True
                    break
                frame = frame.f_back
            
            # Also check environment variables that indicate WSGI mode
            is_wsgi_mode = (
                wsgi_context or
                os.environ.get('WSGI_APPLICATION') is not None or
                'gunicorn' in ' '.join(sys.argv) if sys.argv else False or
                'uwsgi' in ' '.join(sys.argv) if sys.argv else False
            )
            
            # Only start background jobs if we're actually running a server
            if not (is_runserver or is_wsgi_mode):
                return
            
        except Exception:
            # If detection fails, err on the side of caution and don't run
            return
        
        PagesConfig._background_jobs_started = True
        
        # Start background jobs in a separate thread
        thread = threading.Thread(target=self._run_background_jobs, daemon=True)
        thread.start()

    def _run_background_jobs(self):
        """Run background jobs in a separate thread."""
        import time
        
        # Wait for server to be fully ready
        time.sleep(10)
        
        # Wait a bit more for database migrations to complete
        time.sleep(5)
        
        try:
            # Check if catalog needs to be loaded
            catalog_file = os.path.join(os.getcwd(), 'catalog-2025.csv')
            db_loaded_flag = os.path.join(os.getcwd(), 'db_loaded.flag')
            
            if os.path.exists(catalog_file) and not os.path.exists(db_loaded_flag):
                # Load catalog data
                try:
                    call_command('load_catalog', verbosity=0)
                    # Create flag file to prevent reloading
                    with open(db_loaded_flag, 'w') as f:
                        f.write('')
                except Exception as e:
                    print(f'Background job: Failed to load catalog: {e}')
            
            # Download category images (run regardless)
            try:
                call_command('download_category_images', verbosity=0)
            except Exception as e:
                print(f'Background job: Failed to download images: {e}')
            
            # Collect static files (optional - for Django admin static files)
            # With CompressedStaticFilesStorage, collectstatic is optional
            # It mainly collects Django admin static files (CSS, JS, images)
            # Your app's static files are already in git and served directly
            try:
                call_command('collectstatic', '--noinput', verbosity=0)
                print('Background job: Static files collected successfully')
            except Exception as e:
                print(f'Background job: Static files collection failed (non-critical): {e}')
                # Non-critical - WhiteNoise serves from STATICFILES_DIRS directly
                
        except Exception as e:
            print(f'Background jobs error: {e}')

