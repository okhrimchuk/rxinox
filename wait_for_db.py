#!/usr/bin/env python
"""Wait for database to be ready."""
import os
import sys
import time
from django.db import connection
from django.db.utils import OperationalError

def wait_for_db():
    """Wait for database to be available."""
    max_attempts = 30
    attempt = 0
    
    while attempt < max_attempts:
        try:
            connection.ensure_connection()
            print("Database is ready!")
            return True
        except OperationalError:
            attempt += 1
            print(f"Waiting for database... ({attempt}/{max_attempts})")
            time.sleep(1)
    
    print("Database not available after 30 attempts!")
    return False

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rxinox.settings')
    try:
        import django
        django.setup()
        
        if not wait_for_db():
            print("Warning: Database connection failed, but continuing...")
            sys.exit(0)  # Exit with 0 to not fail the startup script
    except Exception as e:
        print(f"Warning: Database check failed: {e}, but continuing...")
        sys.exit(0)  # Exit with 0 to not fail the startup script

