from django.shortcuts import render, get_object_or_404, redirect
from django.utils.text import slugify
from django.db.models import Q, Count
from django.http import JsonResponse
from decimal import Decimal
from .models import Product, Category


def get_cart(request):
    """Get cart from session or initialize empty cart."""
    if 'cart' not in request.session:
        request.session['cart'] = {}
    return request.session['cart']


def get_cart_count(request):
    """Get total number of items in cart."""
    cart = get_cart(request)
    return sum(item['quantity'] for item in cart.values())


def get_cart_context(request):
    """Get cart items with product details."""
    cart = get_cart(request)
    cart_items = []
    grand_total = Decimal('0.00')
    
    for product_code, item_data in cart.items():
        try:
            product = Product.objects.get(product_code=product_code)
            quantity = item_data['quantity']
            unit_price = product.price
            item_total = unit_price * Decimal(str(quantity))
            grand_total += item_total
            
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'unit_price': unit_price,
                'item_total': item_total,
            })
        except Product.DoesNotExist:
            # Product was deleted, skip it
            continue
    
    return {
        'cart_items': cart_items,
        'grand_total': grand_total,
        'cart_count': get_cart_count(request),
    }


def landing_page(request):
    """Landing page view."""
    # Get products grouped by category
    # Categories are stored as full_path in the Category model
    # Get all products with their categories and group by top-level category
    
    # Get all products that have categories
    products = Product.objects.filter(category__isnull=False).select_related('category')
    
    # Group by top-level category name
    top_level_categories = {}
    
    for product in products:
        if not product.category:
            continue
            
        # Extract top-level category name (first part before " > ")
        full_path = product.category.full_path
        top_level = full_path.split(' > ')[0].strip()
        
        if top_level not in top_level_categories:
            # Find first product in this category with an image
            product_with_image = Product.objects.filter(
                category__full_path__startswith=top_level
            ).exclude(
                Q(image_url__isnull=True) | Q(image_url='')
            ).first()
            
            # Get product count for this top-level category
            product_count = Product.objects.filter(
                category__full_path__startswith=top_level
            ).count()
            
            top_level_categories[top_level] = {
                'name': top_level,
                'slug': slugify(top_level),
                'count': product_count,
                'image_url': product_with_image.image_url if product_with_image else ''
            }
    
    context = {
        'categories': list(top_level_categories.values()),
        'cart_count': get_cart_count(request),
    }
    return render(request, 'pages/landing.html', context)


def category_page(request, category_slug):
    """Category page view showing products in a category."""
    # Find category by matching top-level category name slug
    # Get all categories and find one whose top-level name matches the slug
    categories = Category.objects.all()
    
    # Find the category by matching the slugified top-level name
    matching_category = None
    for cat in categories:
        top_level = cat.full_path.split(' > ')[0].strip()
        if slugify(top_level) == category_slug:
            matching_category = top_level
            break
    
    if not matching_category:
        # If not found, try to find by any part of the full path
        for cat in categories:
            if slugify(cat.full_path) == category_slug or slugify(cat.name) == category_slug:
                matching_category = cat.full_path.split(' > ')[0].strip()
                break
    
    if not matching_category:
        # Return 404 if category not found
        from django.http import Http404
        raise Http404("Category not found")
    
    # Get all products in this top-level category (including those without images)
    products = Product.objects.filter(
        category__full_path__startswith=matching_category
    ).select_related('category').order_by('name')
    
    context = {
        'category_name': matching_category,
        'category_slug': category_slug,
        'products': products,
        'product_count': products.count(),
        'cart_count': get_cart_count(request),
    }
    return render(request, 'pages/category.html', context)


def product_page(request, category_slug, product_slug):
    """Product page view showing product details."""
    # Find the category first
    categories = Category.objects.all()
    matching_category = None
    for cat in categories:
        top_level = cat.full_path.split(' > ')[0].strip()
        if slugify(top_level) == category_slug:
            matching_category = top_level
            break
    
    if not matching_category:
        from django.http import Http404
        raise Http404("Category not found")
    
    # Find the product by slug (product name slugified)
    products_in_category = Product.objects.filter(
        category__full_path__startswith=matching_category
    )
    
    product = None
    for p in products_in_category:
        if slugify(p.name) == product_slug:
            product = p
            break
    
    if not product:
        from django.http import Http404
        raise Http404("Product not found")
    
    # Handle add to cart form submission
    error_message = None
    success_message = None
    if request.method == 'POST':
        quantity = request.POST.get('quantity', '').strip()
        try:
            quantity_int = int(quantity)
            if quantity_int > 0:
                # Add to cart
                cart = get_cart(request)
                product_code = product.product_code
                
                if product_code in cart:
                    cart[product_code]['quantity'] += quantity_int
                else:
                    cart[product_code] = {
                        'quantity': quantity_int,
                    }
                
                request.session.modified = True
                from django.contrib import messages
                messages.success(request, f'Añadido al carrito: {quantity_int} unidad(es) de {product.name}')
                success_message = f'Añadido al carrito: {quantity_int} unidad(es)'
                # Redirect to prevent resubmission on refresh
                return redirect('product_page', category_slug=category_slug, product_slug=product_slug)
            else:
                error_message = 'La cantidad debe ser mayor que 0'
        except (ValueError, TypeError):
            error_message = 'Por favor ingrese un número válido'
    
    # Get all images for the product
    images = product.get_images()
    
    context = {
        'product': product,
        'category_name': matching_category,
        'category_slug': category_slug,
        'images': images,
        'error_message': error_message,
        'success_message': success_message,
        'cart_count': get_cart_count(request),
    }
    return render(request, 'pages/product.html', context)


def cart_page(request):
    """Cart page view showing all cart items."""
    cart_context = get_cart_context(request)
    context = {
        'cart_items': cart_context['cart_items'],
        'grand_total': cart_context['grand_total'],
        'cart_count': cart_context['cart_count'],
    }
    return render(request, 'pages/cart.html', context)


def add_to_cart(request):
    """AJAX endpoint to add item to cart."""
    if request.method == 'POST':
        product_code = request.POST.get('product_code')
        quantity = int(request.POST.get('quantity', 1))
        
        try:
            product = Product.objects.get(product_code=product_code)
            cart = get_cart(request)
            
            if product_code in cart:
                cart[product_code]['quantity'] += quantity
            else:
                cart[product_code] = {'quantity': quantity}
            
            request.session.modified = True
            cart_count = get_cart_count(request)
            
            return JsonResponse({
                'success': True,
                'cart_count': cart_count,
                'message': f'Añadido {quantity} unidad(es) al carrito'
            })
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Producto no encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)


def update_cart_item(request, product_code):
    """Update quantity of a cart item."""
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart = get_cart(request)
        
        if product_code in cart:
            if quantity > 0:
                cart[product_code]['quantity'] = quantity
                request.session.modified = True
                return redirect('cart_page')
            else:
                # Remove item if quantity is 0
                del cart[product_code]
                request.session.modified = True
                return redirect('cart_page')
    
    return redirect('cart_page')


def remove_cart_item(request, product_code):
    """Remove item from cart."""
    cart = get_cart(request)
    if product_code in cart:
        del cart[product_code]
        request.session.modified = True
    
    return redirect('cart_page')


def checkout_page(request):
    """Checkout page with contact details form."""
    # Redirect to cart if cart is empty
    cart = get_cart(request)
    if not cart:
        return redirect('cart_page')
    
    error_message = None
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        business_name = request.POST.get('business_name', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        
        # Basic validation
        if not first_name or not last_name or not email or not phone_number:
            error_message = 'Por favor complete todos los campos requeridos'
        else:
            # Store contact details in session
            request.session['checkout_contact'] = {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'business_name': business_name,
                'phone_number': phone_number,
            }
            request.session.modified = True
            return redirect('order_summary_page')
    
    # Pre-fill form if contact details exist in session
    contact_details = request.session.get('checkout_contact', {})
    
    # Get cart context for sidebar
    cart_context = get_cart_context(request)
    
    context = {
        'contact_details': contact_details,
        'error_message': error_message,
        'cart_items': cart_context['cart_items'],
        'grand_total': cart_context['grand_total'],
        'cart_count': get_cart_count(request),
    }
    return render(request, 'pages/checkout.html', context)


def send_order_email_placeholder(contact_details, cart_items, grand_total):
    """
    Placeholder function to send order email to manager.
    For now, this just returns the order data to be displayed in a popup.
    In production, this would send an email using Django's email backend.
    """
    # TODO: Replace with actual email sending functionality
    # Example:
    # from django.core.mail import send_mail
    # subject = f'Nuevo pedido de {contact_details["first_name"]} {contact_details["last_name"]}'
    # message = format_order_email(contact_details, cart_items, grand_total)
    # send_mail(subject, message, 'noreply@rxinox.com', ['manager@rxinox.com'])
    
    # For now, just return the order data
    order_data = {
        'contact_details': contact_details,
        'cart_items': [
            {
                'product_code': item['product'].product_code,
                'product_name': item['product'].name,
                'quantity': item['quantity'],
                'unit_price': str(item['unit_price']),
                'item_total': str(item['item_total']),
                'currency': item['product'].currency,
            }
            for item in cart_items
        ],
        'grand_total': str(grand_total),
    }
    return order_data


def order_summary_page(request):
    """Order summary page showing cart items and contact details."""
    # Redirect to cart if cart is empty
    cart = get_cart(request)
    if not cart:
        return redirect('cart_page')
    
    # Redirect to checkout if contact details are missing
    contact_details = request.session.get('checkout_contact')
    if not contact_details:
        return redirect('checkout_page')
    
    # Get cart context with items and totals
    cart_context = get_cart_context(request)
    
    # Handle order submission
    if request.method == 'POST':
        # Send order email (placeholder)
        order_data = send_order_email_placeholder(
            contact_details,
            cart_context['cart_items'],
            cart_context['grand_total']
        )
        
        # Store order data in session for popup display
        request.session['last_order_data'] = order_data
        request.session.modified = True
        
        # Clear cart and contact details after order submission
        if 'cart' in request.session:
            del request.session['cart']
        if 'checkout_contact' in request.session:
            del request.session['checkout_contact']
        request.session.modified = True
        
        # Redirect to success page with order data
        return redirect('order_success_page')
    
    context = {
        'cart_items': cart_context['cart_items'],
        'grand_total': cart_context['grand_total'],
        'contact_details': contact_details,
        'cart_count': cart_context['cart_count'],
    }
    return render(request, 'pages/order_summary.html', context)


def order_success_page(request):
    """Order success page showing confirmation and order details popup."""
    order_data = request.session.get('last_order_data')
    
    if not order_data:
        # If no order data, redirect to landing page
        return redirect('landing_page')
    
    context = {
        'order_data': order_data,
        'cart_count': get_cart_count(request),
    }
    return render(request, 'pages/order_success.html', context)

