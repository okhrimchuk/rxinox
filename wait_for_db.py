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
    import django
    django.setup()
    
    if not wait_for_db():
        sys.exit(1)

