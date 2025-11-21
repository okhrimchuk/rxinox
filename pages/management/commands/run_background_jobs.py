"""
Background jobs that run after server startup.
This command can be called manually or triggered automatically.
"""
import os
import sys
import threading
import time
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection


class Command(BaseCommand):
    help = 'Run background jobs (catalog loading, image downloading, etc.)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--load-catalog',
            action='store_true',
            help='Load catalog data from CSV file'
        )
        parser.add_argument(
            '--download-images',
            action='store_true',
            help='Download category images'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Run all background jobs'
        )
        parser.add_argument(
            '--wait-for-db',
            type=int,
            default=5,
            help='Wait N seconds for database to be ready (default: 5)'
        )

    def handle(self, *args, **options):
        # Wait a bit for database to be fully ready
        wait_time = options.get('wait_for_db', 5)
        if wait_time > 0:
            self.stdout.write(f'Waiting {wait_time} seconds for database to be ready...')
            time.sleep(wait_time)
        
        # Ensure database connection is alive
        try:
            connection.ensure_connection()
            self.stdout.write(self.style.SUCCESS('Database connection verified'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Database connection failed: {e}'))
            return

        run_all = options.get('all', False)
        load_catalog = options.get('load_catalog', False) or run_all
        download_images = options.get('download_images', False) or run_all

        if not load_catalog and not download_images:
            self.stdout.write(self.style.WARNING('No jobs specified. Use --all, --load-catalog, or --download-images'))
            return

        self.stdout.write('Starting background jobs...')

        # Run catalog loading if requested
        if load_catalog:
            self.stdout.write('\n--- Loading catalog data ---')
            try:
                call_command('load_catalog', verbosity=1)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Failed to load catalog: {e}'))

        # Run image downloading if requested
        if download_images:
            self.stdout.write('\n--- Downloading category images ---')
            try:
                call_command('download_category_images', verbosity=1)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Failed to download images: {e}'))

        self.stdout.write(self.style.SUCCESS('\nBackground jobs completed'))

