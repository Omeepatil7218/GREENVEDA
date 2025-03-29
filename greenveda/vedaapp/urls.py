from django.urls import path
from . import views
from xml.dom.minidom import Document
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from .views import order_history, order_detail
from .views import profile_view  # Updated import


urlpatterns = [
    # urls.py
    path('admin/orders/<int:order_id>/complete/', views.mark_order_completed, name='mark_order_completed'),
    # ... your other URLs ...
    path('orders/<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),
    path('orders/', views.order_history, name='order_history'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('update-avatar/', views.update_avatar, name='update_avatar'),  # Add this line
    path('update-profile/', views.update_profile, name='update_profile'),

    path('orders/', views.order_history, name='order_history'),  # ✅ Fix: Add this URL pattern
    path('profile/', views.profile_view, name='profile'),

    path('', views.index, name='index'),  # Root URL
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('blog/', views.blog, name='blog'),
    path('product/', views.products, name='products'),
    # path('feature/', views.feature, name='feature'),
    # path('testimonial/', views.testimonial, name='testimonial'),
    path('products/', views.product_list, name='product_list'),
    path('product/view/<int:prod_id>/', views.view, name='view'),
    path('customer-details/', views.customer_details, name='customer_details'),
    # path('medicines/', views.medicines_view, name='medicines'),

    path('products/category/<int:category_id>/', views.product_by_category, name='product_by_category'),
    path('medicines/', views.medicines, name='medicines'),  # Default medicines page
    path('medicines/<int:category_id>/', views.medicines, name='medicines'),  # Category filter
    path('category_products/<int:cat_id>/', views.category_products, name='category_products'),  # Fix the pattern

    path('payment', views.payment, name='payment'),
    path('payment-confirm', views.payment_confirm, name='paymentconfirm'),
    # path('category/<int:category_id>/', views.category_detail, name='category_detail'),
    # path('category/<int:cat_id>/', views.view_category, name='view_category'),
    path('features/', views.features_view, name='features'),

    path('cart/', views.cart, name='cart'),  # Ensure the name is correct
    path('add_to_cart/<int:prod_id>/', views.add_to_cart, name='add_to_cart'),
    path('increase_quantity/<int:product_id>/', views.increase_quantity, name='increase_quantity'),
    path('decrease_quantity/<int:product_id>/', views.decrease_quantity, name='decrease_quantity'),
    path('remove_from_cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('filter-products/', views.filter_products, name='filter_products'),

    path('change-password/', views.change_password, name='change_password'),



    path('login/', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name='logout'),
    # path('profile/', views.profile, name='profile'),

    path('register/', views.register, name='register'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
