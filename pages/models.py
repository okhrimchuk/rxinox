from django.db import models
import json


class Category(models.Model):
    """Product category model."""
    name = models.CharField(max_length=255)  # Category name (last part of path)
    full_path = models.CharField(max_length=500, unique=True)  # Full category path like "Glass clamps > GC For flat > Glass clamps 40 x 50 mm"
    slug = models.SlugField(max_length=255, blank=True)
    parent_path = models.CharField(max_length=500, blank=True)  # Parent category path if hierarchical
    image_url = models.URLField(max_length=1000, blank=True)  # URL to category image
    image = models.ImageField(upload_to='categories/', blank=True, null=True)  # Downloaded category image
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['full_path']
    
    def __str__(self):
        return self.full_path
    
    def get_image_url(self):
        """Return the local image if available, otherwise the original URL."""
        if self.image:
            return self.image.url
        return self.image_url


class Product(models.Model):
    """Product model."""
    product_code = models.CharField(max_length=100, unique=True)
    active = models.BooleanField(default=True)
    name = models.CharField(max_length=500)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    vat = models.CharField(max_length=20, blank=True)
    unit = models.CharField(max_length=50, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    barcode = models.CharField(max_length=100, blank=True)
    weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    producer = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    short_description = models.TextField(blank=True)
    stock = models.IntegerField(default=0)
    availability = models.CharField(max_length=100, blank=True)
    delivery = models.CharField(max_length=100, blank=True)
    currency = models.CharField(max_length=10, default='EUR')
    seo_url = models.CharField(max_length=255, blank=True)
    image_url = models.URLField(max_length=500, blank=True)  # First product image URL
    images_json = models.TextField(blank=True)  # JSON array of all image URLs (images 1-15)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_images(self):
        """Return list of image URLs."""
        if self.images_json:
            try:
                return json.loads(self.images_json)
            except json.JSONDecodeError:
                return []
        # Fallback to image_url if images_json is empty
        if self.image_url:
            return [self.image_url]
        return []
    
    def get_slug(self):
        """Generate slug from product name."""
        from django.utils.text import slugify
        return slugify(self.name)

