from profile import Profile
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.template.loader import render_to_string
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from jsonschema import ValidationError
from .models import PlantMaster, CategoryMaster, Feature, UserMaster
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .models import CartMaster, CustomerMaster, PlantMaster, Feature, CategoryMaster

# ----------------------------- Home Page ---------------------------------
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.core.files.images import get_image_dimensions
from django.core.exceptions import ValidationError
from .models import UserProfile

@login_required 
def profile_view(request):
    profile = get_object_or_404(UserProfile, user=request.user)

    """Handle profile display and updates"""
    if request.method == 'POST':
        return handle_profile_update(request)
    return render(request, 'profile.html')

def handle_profile_update(request):
    """Centralized profile update handling"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if 'avatar' in request.FILES:
        return handle_avatar_update(request, profile)
    
    # Update user fields
    user = request.user
    user.first_name = request.POST.get('first_name', user.first_name)
    user.last_name = request.POST.get('last_name', user.last_name)
    user.save()
    
    # Update profile fields
    update_fields = [
        'phone', 'gender', 'dob', 'language',
        'address', 'city', 'state', 'pincode'
    ]
    
    for field in update_fields:
        if field in request.POST:
            setattr(profile, field, request.POST.get(field))
    
    profile.save()
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'full_name': user.get_full_name()
        })
    
    messages.success(request, 'Profile updated successfully!')
    return redirect('profile')

def handle_avatar_update(request, profile=None):
    """Handle avatar uploads with validation"""
    if profile is None:
        profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    avatar = request.FILES['avatar']
    
    try:
        # Validate image
        if avatar.size > 5 * 1024 * 1024:
            raise ValidationError('Image size should not exceed 5MB')
        
        w, h = get_image_dimensions(avatar)
        if w > 2000 or h > 2000:
            raise ValidationError('Image dimensions too large (max 2000x2000)')
        
        profile.avatar = avatar
        profile.save()
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'avatar_url': profile.avatar.url
            })
        
        messages.success(request, 'Profile picture updated successfully!')
        return redirect('profile')
    
    except Exception as e:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
        
        messages.error(request, str(e))
        return redirect('profile')
    
    # vedaapp/views.py
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

@login_required
def update_avatar(request):
    if request.method == 'POST' and request.FILES.get('avatar'):
        try:
            profile = request.user.profile
            avatar = request.FILES['avatar']
            
            # Validate image size (5MB limit)
            if avatar.size > 5 * 1024 * 1024:
                return JsonResponse({
                    'success': False,
                    'error': 'Image size should not exceed 5MB'
                })
            
            profile.avatar = avatar
            profile.save()
            
            return JsonResponse({
                'success': True,
                'avatar_url': profile.avatar.url
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request'
    })
# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

@login_required
def update_profile(request):
    if request.method == 'POST':
        try:
            profile = request.user.profile
            data = request.POST
            
            # Update user fields
            request.user.first_name = data.get('first_name', request.user.first_name)
            request.user.last_name = data.get('last_name', request.user.last_name)
            request.user.save()
            
            # Update profile fields
            profile_fields = ['phone', 'gender', 'dob', 'language', 
                            'address', 'city', 'state', 'pincode']
            for field in profile_fields:
                if field in data:
                    setattr(profile, field, data[field])
            
            profile.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Profile updated successfully',
                'full_name': request.user.get_full_name()
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    }, status=405)
from django.shortcuts import render

def order_history(request):
    """Simple Order History View"""
    return render(request, 'order_history.html')

def index(request):
    """
    Renders the home page with all categories, selected category products, and features.
    """
    categories = CategoryMaster.objects.all()
    selected_category_id = request.GET.get('category_id', None)

    if selected_category_id:
        products = PlantMaster.objects.filter(category__catID=selected_category_id)
    else:
        products = PlantMaster.objects.all()

    features = Feature.objects.all()

    return render(request, 'index.html', {
        'products': products,
        'features': features,
        'categories': categories,
        'active_menu': '/',
        'selected_category_id': str(selected_category_id) if selected_category_id else None,
    })

# ----------------------------- About Page ---------------------------------
def about(request):
    """
    Renders the about page with all available features.
    """
    features = Feature.objects.all()
    return render(request, 'about.html', {'features': features})

# ----------------------------- Contact Page ---------------------------------
def contact(request):
    """
    Renders the contact page.
    """
    return render(request, 'contact.html')

# ----------------------------- Blog Page ---------------------------------
def blog(request):
    """
    Renders the blog page.
    """
    return render(request, 'blog.html')

# ----------------------------- Product Filtering (Ajax) ---------------------------------
def filter_products(request):
    """
    Returns filtered products based on the selected category (Ajax request).
    """
    category_id = request.GET.get('category_id', None)
    if category_id:
        products = PlantMaster.objects.filter(category__catID=category_id)
    else:
        products = PlantMaster.objects.all()

    html = render_to_string('index.html', {'products': products}, request=request)
    return JsonResponse({'html': html})
# ----------------------------- Products Page ---------------------------------
def products(request):
    """
    Displays all products except those in the 'Medicine' category.
    """
    category_id = request.GET.get('category_id', None)
    categories = CategoryMaster.objects.exclude(catName="medicines")

    if category_id:
        products = PlantMaster.objects.filter(category__catID=category_id)
    else:
        products = PlantMaster.objects.all()

    products = products.exclude(category__catName="medicines")

    return render(request, 'product.html', {
        'products': products,
        'categories': categories,
        'selected_category_id': category_id
    })

# ----------------------------- Product by Category ---------------------------------
def product_by_category(request, category_id):
    """
    Retrieves products for a specific category.
    """
    category = get_object_or_404(CategoryMaster, id=category_id)
    products = PlantMaster.objects.filter(category=category)
    categories = CategoryMaster.objects.all()

    return render(request, 'product.html', {
        'products': products,
        'categories': categories,
        'selected_category': category
    })
# ----------------------------- Cart Management ---------------------------------
def cart(request):
    """
    Displays cart items for the logged-in user.
    """
    cart_items = CartMaster.objects.filter(user=request.user)
    total_cost = sum(item.price * item.qty for item in cart_items)

    products = [{
        'id': item.product.id,
        'name': item.product.name,
        'price': item.price,
        'quantity': item.qty,
        'total': item.price * item.qty,
        'image': item.product.image.url if item.product.image else 'static/img/default-product.png',
    } for item in cart_items]

    return render(request, 'cart.html', {'products': products, 'total_cost': total_cost})

def add_to_cart(request, prod_id):
    """
    Adds a product to the cart or updates its quantity.
    """
    if request.user.is_authenticated:
        product = get_object_or_404(PlantMaster, id=prod_id)
        cart_item, created = CartMaster.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={'qty': 1, 'price': product.price, 'subtotal': product.price}
        )

        if not created:
            cart_item.qty += 1
            cart_item.subtotal = cart_item.qty * cart_item.price
            cart_item.save()

        return redirect('cart')
    else:
        return redirect(f"{reverse('user_login')}?next={request.path}")

def increase_quantity(request, product_id):
    """
    Increases the quantity of a cart item.
    """
    cart_item = get_object_or_404(CartMaster, product_id=product_id, user=request.user)
    cart_item.qty += 1
    cart_item.subtotal = cart_item.qty * cart_item.product.price
    cart_item.save()
    return redirect('cart')

def decrease_quantity(request, product_id):
    """
    Decreases the quantity of a cart item but ensures it remains at least 1.
    """
    cart_item = get_object_or_404(CartMaster, product_id=product_id, user=request.user)
    if cart_item.qty > 1:
        cart_item.qty -= 1
        cart_item.subtotal = cart_item.qty * cart_item.product.price
        cart_item.save()
    return redirect('cart')

def remove_from_cart(request, product_id):
    """
    Removes an item from the cart.
    """
    try:
        cart_item = CartMaster.objects.get(product=product_id, user=request.user)
        cart_item.delete()
    except CartMaster.DoesNotExist:
        pass
    return redirect('cart')

# ----------------------------- Product Details ---------------------------------
def view(request, prod_id):
    """
    Displays detailed information about a selected product.
    """
    product = PlantMaster.objects.get(id=prod_id)
    return render(request, 'view.html', {'product': product})

# ----------------------------- Customer Details ---------------------------------
def customer_details(request):
    """
    Captures customer details and saves them for the order.
    """
    last_three_addresses = CustomerMaster.objects.order_by('-customerID')[:3]

    if request.method == 'POST':
        print(request.POST)  # Debugging line to check if form data is received

        customer_name = request.POST.get('customerName')
        email = request.POST.get('email')
        contact = request.POST.get('contact')
        address = request.POST.get('address')
        pincode = request.POST.get('pincode')

        # Ensure customerName is not empty
        if not customer_name:
            return render(request, 'customer_details.html', {'error': 'Customer Name is required!', 'last_three_addresses': last_three_addresses})

        customer = CustomerMaster(
            customerName=customer_name,
            email=email,
            contact=contact,
            address=address,
            pincode=pincode,
        )
        customer.save()

        request.session['customername'] = customer.customerName
        request.session['email'] = customer.email
        request.session['contact'] = customer.contact
        request.session['address'] = customer.address
        request.session['pincode'] = customer.pincode

        return redirect('payment')

    return render(request, 'customer_details.html', {'last_three_addresses': last_three_addresses})

# ----------------------------- Payment Process ---------------------------------
def payment(request):
    """
    Handles the payment process.
    """
    cart_items = CartMaster.objects.filter(user=request.user)
    total_price = sum(item.subtotal for item in cart_items)

    if request.method == "POST":
        payment_method = request.POST.get('payment_method')
        if payment_method:
            return HttpResponse(f"Processing {payment_method} payment... Total: ₹{total_price}")
        else:
            return HttpResponse("Please select a payment method.")

    return render(request, 'payment.html', {'total_price': total_price, 'cart_items': cart_items})

# ----------------------------- Payment Confirmation ---------------------------------
from django.shortcuts import render, redirect
from .models import CartMaster
def view(request, prod_id):
    """
    View to display details of a specific product.
    """
    product = PlantMaster.objects.get(id=prod_id)
    return render(request, 'view.html', {'product': product})
# views.py
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from .models import CartMaster, Order, OrderItem

def payment_confirm(request):
    """
    Creates an order from cart items with 'pending' status first,
    then updates to 'processing' after payment confirmation.
    """
    if request.method == "POST" and request.user.is_authenticated:
        cart_items = CartMaster.objects.filter(user=request.user)
        
        if cart_items.exists():
            total_price = sum(item.price * item.qty for item in cart_items)
            
            # Create order with 'pending' status first
            order = Order.objects.create(
                user=request.user,
                total_price=total_price,
                status='pending'  # Initial status
            )
            
            # Create order items
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.qty,
                    price=item.price
                )
            
            # Process payment (replace with your actual payment logic)
            payment_successful = True  # This should come from your payment gateway
            
            if payment_successful:
                # Update status to 'processing' after successful payment
                order.status = 'processing'
                order.save()
                
                # Clear cart only after successful payment
                cart_items.delete()
                
                last_order = Order.objects.filter(
                    user=request.user
                ).order_by('-created_at').first()
                
                return render(request, 'paymentconfirm.html', {
                    'show_home_button': True,
                    'last_order': last_order
                })
            else:
                # Payment failed - keep order as 'pending'
                return render(request, 'payment_failed.html', {
                    'order': order
                })
    
    return redirect('index')
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def mark_order_completed(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if order.status == 'processing':
        order.status = 'completed'
        order.save()
        messages.success(request, f"Order #{order.id} marked as completed")
    return redirect('admin:orders_order_changelist')
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Order
from django.http import JsonResponse
from django.views.decorators.http import require_POST

def cancel_order(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        
        # Check if order can be cancelled
        if order.status not in ['pending', 'processing']:
            return JsonResponse({
                'success': False,
                'message': 'Order cannot be cancelled at this stage'
            }, status=400)
            
        # Update order status
        order.status = 'cancelled'
        order.save()
        
        # Here you might want to add:
        # 1. Send cancellation email
        # 2. Restock products if needed
        # 3. Create cancellation record
        
        return JsonResponse({'success': True})
        
    except Order.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Order not found'
        }, status=404)
def order_history(request):
    """
    Displays paginated order history for the logged-in user
    """
    orders_list = Order.objects.filter(user=request.user).order_by('-created_at')
    
    # Pagination - 10 orders per page
    paginator = Paginator(orders_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'order_history.html', {
        'orders': page_obj,
        'page_obj': page_obj,
        'is_paginated': paginator.num_pages > 1
    })

def order_detail(request, order_id):
    """
    Shows details of a specific order
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_detail.html', {'order': order})

##### PRODUCT VIEWS #####
def product_list(request):
    """
    View to list products from specific allowed categories (herbs, plants, herbal products)
    """
    category_id = request.GET.get('category_id', None)
    
    # Define excluded and included categories
    excluded_categories = ["medicines", "hair care", "cancer", "diabetiese", "cold", "fever"]
    included_categories = ["herbs", "plants", "herbal products"]  # Add your specific allowed categories
    
    # Get categories - only show allowed categories in filter
    categories = CategoryMaster.objects.filter(catName__in=included_categories)
    
    # Base queryset - only include products from allowed categories
    products = PlantMaster.objects.filter(category__catName__in=included_categories)
    
    # Further filter if specific category is selected
    if category_id:
        products = products.filter(category__catID=category_id)
        # Ensure the selected category is actually in our included categories
        if not categories.filter(catID=category_id).exists():
            category_id = None  # Reset if invalid category selected
    
    return render(request, 'product.html', {
        'products': products,
        'categories': categories,
        'selected_category_id': category_id
    })
def medicines(request):
    """
    View to display only "Skin Care", "Hair Care", "Cancer", and "Diabetes" category products.
    """
    allowed_categories = ["skin care", "hair care", "cancer", "diabetiese","cold","fever"]
    
    # Fetch categories matching the allowed names
    selected_categories = CategoryMaster.objects.filter(catName__in=allowed_categories)
    
    if not selected_categories.exists():
        return render(request, 'medicines.html', {
            'products': [],
            'categories': [],
            'selected_category_id': None
        })
    
    category_id = request.GET.get('category_id', None)
    products = PlantMaster.objects.filter(category__in=selected_categories)
    
    if category_id:
        products = products.filter(category__catID=category_id)
    
    return render(request, 'medicines.html', {
        'products': products,
        'categories': selected_categories,
        'selected_category_id': category_id
    })
from .models import PlantMaster, CategoryMaster
from django.shortcuts import render, get_object_or_404
from .models import CategoryMaster, PlantMaster

from django.shortcuts import render, get_object_or_404
from .models import CategoryMaster, PlantMaster

def category_products(request, cat_id):
    """
    View to display products of a specific category.
    """
    selected_category = get_object_or_404(CategoryMaster, catID=cat_id)
    
    products = PlantMaster.objects.filter(category=selected_category)

    return render(request, 'medicines.html', {
        'products': products,
        'categories': CategoryMaster.objects.filter(catName__in=["skin care", "hair care", "cancer", "diabetiese","cold","fever"]),
        'selected_category_id': cat_id
    })

##### FEATURE VIEWS #####

def features_view(request):
    """
    View to fetch and display all features on the homepage.
    """
    features = Feature.objects.all()
    return render(request, 'index.html', {'features': features})


##### USER AUTHENTICATION #####

def user_login(request):
    """
    User login view.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            request.session['username'] = username
            return redirect('index')
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password', 'next': 'index'})
    
    return render(request, 'login.html', {'next': 'cart'})


def user_logout(request):
    """
    User logout view.
    """
    logout(request)
    return redirect('index')


def change_password(request):
    """
    View to handle user password change.
    """
    if request.method == 'POST':
        user = request.user
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not user.check_password(old_password):
            messages.error(request, "The old password is incorrect.")
        elif new_password != confirm_password:
            messages.error(request, "New password and confirm password do not match.")
        elif old_password == new_password:
            messages.error(request, "The new password cannot be the same as the old password.")
        else:
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password was successfully updated!")
            return redirect('index')
    
    return render(request, 'change_password.html')


def user_profile(request):
    """
    View to display and update user profile details.
    """
    user_master = UserMaster.objects.get(userID=request.user.id)
    if request.method == "GET":
        user_master.userName = request.GET.get("userName")
        user_master.email = request.GET.get("email")
        user_master.contact = request.GET.get("contact")
        user_master.save()
    
    return render(request, 'profile.html', {'User_master': user_master})


def register(request):
    """
    User registration view.
    """
    if request.method == 'GET':
        return render(request, "register.html")
    else:
        nm = request.POST['uname']
        p = request.POST['upass']
        cp = request.POST['ucpass']
        context = {}

        if p != cp:
            context['error'] = 'Passwords Do Not Match'
        elif len(p) > 8:
            context['error'] = 'Password should have less than 8 characters'
        else:
            try:
                u = User.objects.create(username=nm)
                u.set_password(p)
                u.save()
                context['success'] = "Successfully Registered"
            except:
                context['error'] = 'User already exists!'
        
        return render(request, "login.html", context)
