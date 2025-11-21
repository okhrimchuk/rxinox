def cart_context(request):
    """Context processor to make cart count available in all templates."""
    from .views import get_cart_count
    from django.utils.text import slugify
    from .models import Product, Category
    
    # Get top-level categories for menu
    top_level_categories = {}
    products = Product.objects.filter(category__isnull=False).select_related('category')
    
    for product in products:
        if not product.category:
            continue
        full_path = product.category.full_path
        top_level = full_path.split(' > ')[0].strip()
        
        if top_level not in top_level_categories:
            top_level_categories[top_level] = {
                'name': top_level,
                'slug': slugify(top_level),
            }
    
    return {
        'cart_count': get_cart_count(request),
        'menu_categories': list(top_level_categories.values()),
    }

