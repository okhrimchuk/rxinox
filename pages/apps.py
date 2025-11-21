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
        
        # Skip if DISABLE_BACKGROUND_JOBS is set
        if os.environ.get('DISABLE_BACKGROUND_JOBS') == 'true':
            return
        
        # Prevent running multiple times
        if PagesConfig._background_jobs_started:
            return
        
        # Check if we're running a management command (skip background jobs)
        if len(sys.argv) > 1 and sys.argv[1] in ['migrate', 'makemigrations', 'collectstatic', 'load_catalog', 'download_category_images', 'createsuperuser', 'shell', 'test', 'run_background_jobs']:
            return
        
        # Only run background jobs in WSGI/ASGI mode or runserver
        # Detection methods:
        # 1. Check for runserver in sys.argv (development)
        # 2. Check if this is WSGI mode (production - gunicorn/uwsgi)
        #    In WSGI mode, sys.argv won't have 'gunicorn', but Django is loaded differently
        # 3. Check for WSGI_APPLICATION in environment
        # 4. Check if we're in a production-like environment
        
        is_runserver = 'runserver' in ' '.join(sys.argv)
        is_wsgi_mode = (
            os.environ.get('WSGI_APPLICATION') is not None or
            'gunicorn' in ' '.join(sys.argv) or
            'uwsgi' in ' '.join(sys.argv) or
            # If no management command is detected and we're not in a test environment
            (len(sys.argv) == 1 and not os.environ.get('PYTEST_CURRENT_TEST'))
        )
        
        # Only run if it's a server (runserver or WSGI), not a management command
        if not (is_runserver or is_wsgi_mode):
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
                
        except Exception as e:
            print(f'Background jobs error: {e}')

