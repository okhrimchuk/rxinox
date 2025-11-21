from django.contrib import admin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['full_path', 'name', 'product_count']
    search_fields = ['name', 'full_path']
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_code', 'name', 'category', 'price', 'stock', 'active']
    list_filter = ['active', 'category', 'producer']
    search_fields = ['product_code', 'name', 'description']
    list_editable = ['active']


