from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('categoria/<slug:category_slug>/', views.category_page, name='category_page'),
    path('categoria/<slug:category_slug>/<slug:product_slug>/', views.product_page, name='product_page'),
    path('carrito/', views.cart_page, name='cart_page'),
    path('carrito/agregar/', views.add_to_cart, name='add_to_cart'),
    path('carrito/actualizar/<str:product_code>/', views.update_cart_item, name='update_cart_item'),
    path('carrito/eliminar/<str:product_code>/', views.remove_cart_item, name='remove_cart_item'),
    path('checkout/', views.checkout_page, name='checkout_page'),
    path('resumen-pedido/', views.order_summary_page, name='order_summary_page'),
    path('pedido-exitoso/', views.order_success_page, name='order_success_page'),
]

