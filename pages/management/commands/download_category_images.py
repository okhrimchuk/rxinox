import os
import requests
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from pages.models import Category, Product
from urllib.parse import urlparse


class Command(BaseCommand):
    help = 'Download category images from product image URLs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force re-download even if image already exists'
        )

    def handle(self, *args, **options):
        self.stdout.write('Downloading category images...')
        
        categories_updated = 0
        categories_skipped = 0
        categories_failed = 0
        
        # Get all categories
        categories = Category.objects.all()
        
        for category in categories:
            # Skip if image already exists and not forcing
            if category.image and not options['force']:
                categories_skipped += 1
                continue
            
            # Get image URL from category or from first product in category
            image_url = category.image_url
            
            if not image_url:
                # Try to get image from first product in this category
                first_product = Product.objects.filter(category=category, image_url__isnull=False).exclude(image_url='').first()
                if first_product:
                    image_url = first_product.image_url
                    # Update category with this image URL
                    category.image_url = image_url
                    category.save()
            
            if not image_url:
                self.stdout.write(
                    self.style.WARNING(f'No image URL found for category: {category.full_path}')
                )
                categories_failed += 1
                continue
            
            try:
                # Download the image
                response = requests.get(image_url, timeout=10, stream=True)
                response.raise_for_status()
                
                # Get file extension from URL
                parsed_url = urlparse(image_url)
                path = parsed_url.path
                ext = os.path.splitext(path)[1] or '.jpg'
                
                # Generate filename
                filename = f'categories/{category.slug or "category"}-{category.id}{ext}'
                
                # Save to Django storage
                file_content = ContentFile(response.content)
                category.image.save(filename, file_content, save=True)
                
                categories_updated += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Downloaded image for: {category.full_path}')
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to download image for {category.full_path}: {e}')
                )
                categories_failed += 1
                continue
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nDownload complete:\n'
                f'  Categories updated: {categories_updated}\n'
                f'  Categories skipped: {categories_skipped}\n'
                f'  Categories failed: {categories_failed}'
            )
        )
