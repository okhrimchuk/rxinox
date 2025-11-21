import csv
import os
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from pages.models import Category, Product
from decimal import Decimal, InvalidOperation


class Command(BaseCommand):
    help = 'Load product catalog from CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='catalog-2025.csv',
            help='Path to the CSV file (default: catalog-2025.csv)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing categories and products before loading'
        )

    def handle(self, *args, **options):
        file_path = options['file']
        
        # Use project root if relative path
        if not os.path.isabs(file_path):
            from django.conf import settings
            file_path = os.path.join(settings.BASE_DIR, file_path)
        
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))
            return
        
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            Product.objects.all().delete()
            Category.objects.all().delete()
        
        self.stdout.write(f'Loading catalog from {file_path}...')
        
        categories_created = 0
        products_created = 0
        products_updated = 0
        
        # First pass: collect all unique categories and their image URLs
        categories_dict = {}
        category_images = {}  # Store image URL for each category
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                category_path = row.get('category', '').strip()
                if category_path:
                    # Extract image 1 URL for this category
                    image_url = row.get('images 1', '').strip()
                    if image_url and category_path not in category_images:
                        category_images[category_path] = image_url
                    
                    if category_path not in categories_dict:
                        # Extract category name (last part of path)
                        category_parts = [p.strip() for p in category_path.split('>')]
                        category_name = category_parts[-1]
                        parent_path = ' > '.join(category_parts[:-1]) if len(category_parts) > 1 else ''
                        
                        slug = slugify(category_path)
                        if not slug:
                            slug = slugify(category_name)
                        
                        # Make slug unique if needed
                        base_slug = slug
                        counter = 1
                        while Category.objects.filter(slug=slug).exclude(full_path=category_path).exists():
                            slug = f"{base_slug}-{counter}"
                            counter += 1
                        
                        try:
                            category = Category.objects.get(full_path=category_path)
                            # Update slug if it's empty
                            if not category.slug:
                                category.slug = slug
                                category.save()
                            created = False
                        except Category.DoesNotExist:
                            category = Category.objects.create(
                                full_path=category_path,
                                name=category_name,
                                parent_path=parent_path,
                                slug=slug,
                                image_url=category_images.get(category_path, ''),
                            )
                            created = True
                            categories_created += 1
                        else:
                            # Update image_url if category exists but doesn't have one
                            if image_url and not category.image_url:
                                category.image_url = image_url
                                category.save()
                        
                        categories_dict[category_path] = category
        
        self.stdout.write(f'Created/Found {len(categories_dict)} categories')
        
        # Second pass: create products
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                try:
                    product_code = row.get('product_code', '').strip()
                    if not product_code:
                        continue
                    
                    category_path = row.get('category', '').strip()
                    category = categories_dict.get(category_path) if category_path else None
                    
                    # Parse price
                    price_str = row.get('price', '0').strip().replace(',', '.')
                    try:
                        price = Decimal(price_str)
                    except (InvalidOperation, ValueError):
                        price = Decimal('0')
                    
                    # Parse weight
                    weight_str = row.get('weight', '').strip().replace(',', '.')
                    weight = None
                    if weight_str:
                        try:
                            weight = Decimal(weight_str)
                        except (InvalidOperation, ValueError):
                            weight = None
                    
                    # Parse stock
                    stock_str = row.get('stock', '0').strip()
                    try:
                        stock = int(stock_str)
                    except (ValueError, TypeError):
                        stock = 0
                    
                    # Parse active
                    active = row.get('active', '1').strip() == '1'
                    
                    # Extract all image URLs (images 1-15)
                    import json
                    image_urls = []
                    for i in range(1, 16):
                        img_url = row.get(f'images {i}', '').strip()
                        if img_url:
                            image_urls.append(img_url)
                    
                    # First image URL for backwards compatibility
                    image_url = image_urls[0] if image_urls else ''
                    
                    # Store all images as JSON
                    images_json = json.dumps(image_urls) if image_urls else ''
                    
                    product, created = Product.objects.update_or_create(
                        product_code=product_code,
                        defaults={
                            'active': active,
                            'name': row.get('name', '').strip(),
                            'price': price,
                            'vat': row.get('vat', '').strip(),
                            'unit': row.get('unit', '').strip(),
                            'category': category,
                            'barcode': row.get('barcode', '').strip(),
                            'weight': weight,
                            'producer': row.get('producer', '').strip(),
                            'description': row.get('description', '').strip(),
                            'short_description': row.get('short_description', '').strip(),
                            'stock': stock,
                            'availability': row.get('availability', '').strip(),
                            'delivery': row.get('delivery', '').strip(),
                            'currency': row.get('currency', 'EUR').strip(),
                            'seo_url': row.get('seo_url', '').strip(),
                            'image_url': image_url,
                            'images_json': images_json,
                        }
                    )
                    
                    # Update category image_url if it doesn't have one and this product has an image
                    if category and image_url and not category.image_url:
                        category.image_url = image_url
                        category.save()
                    
                    if created:
                        products_created += 1
                    else:
                        products_updated += 1
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f'Error processing row: {e}')
                    )
                    continue
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully loaded catalog:\n'
                f'  Categories created: {categories_created}\n'
                f'  Products created: {products_created}\n'
                f'  Products updated: {products_updated}'
            )
        )

