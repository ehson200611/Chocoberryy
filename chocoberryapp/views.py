# chocoberryapp/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .models import Product, Location, Order, OrderItem, CustomUser
from .forms import ContactForm, OrderForm, CustomUserCreationForm, CustomAuthenticationForm

def home(request):
    featured_products = Product.objects.filter(is_popular=True)[:4] or Product.objects.all()[:4]
    new_products = Product.objects.filter(is_new=True)[:3]
    return render(request, 'chocoberryapp/home.html', {
        'featured_products': featured_products,
        'new_products': new_products
    })

def menu(request):
    query = request.GET.get('q')
    category_filter = request.GET.get('category')
    
    products = Product.objects.all()
    
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(category__icontains=query)
        )
    
    if category_filter and category_filter != 'all':
        products = products.filter(category=category_filter)
    
    categories = Product.objects.values_list('category', flat=True).distinct()
    
    cart_items_count = 0
    if 'cart' in request.session:
        cart = request.session['cart']
        cart_items_count = sum(item['quantity'] for item in cart.values())
    
    return render(request, 'chocoberryapp/menu.html', {
        'products': products, 
        'categories': categories,
        'search_query': query,
        'selected_category': category_filter,
        'cart_items_count': cart_items_count
    })

def locations(request):
    locations = Location.objects.all()
    return render(request, 'chocoberryapp/locations.html', {'locations': locations})

def about(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'chocoberryapp/about.html', {
                'form': ContactForm(),
                'success_message': 'Thank you for your message! We will contact you soon.'
            })
    else:
        form = ContactForm()
    
    return render(request, 'chocoberryapp/about.html', {'form': form})

# Auth Views
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to Chocoberry!')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'chocoberryapp/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'chocoberryapp/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

@login_required
def profile_view(request):
    if request.method == 'POST':
        # Барои навсозии профил
        user = request.user
        user.email = request.POST.get('email')
        user.phone = request.POST.get('phone')
        user.address = request.POST.get('address')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    
    return render(request, 'chocoberryapp/profile.html')

# Cart Views
def view_cart(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0
    
    for product_id, item in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            item_total = product.price * item['quantity']
            cart_items.append({
                'product': product,
                'quantity': item['quantity'],
                'total': item_total
            })
            total_price += item_total
        except Product.DoesNotExist:
            continue
    
    return render(request, 'chocoberryapp/cart.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })

def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        cart = request.session.get('cart', {})
        
        if str(product_id) in cart:
            cart[str(product_id)]['quantity'] += 1
        else:
            cart[str(product_id)] = {
                'quantity': 1,
                'name': product.name,
                'price': str(product.price)
            }
        
        request.session['cart'] = cart
        request.session.modified = True
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            cart_items_count = sum(item['quantity'] for item in cart.values())
            return JsonResponse({
                'success': True,
                'cart_items_count': cart_items_count,
                'message': f'{product.name} added to cart!'
            })
        
        return redirect('menu')
    
    return redirect('menu')

def update_cart(request, product_id):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity <= 0:
            if str(product_id) in cart:
                del cart[str(product_id)]
        else:
            if str(product_id) in cart:
                cart[str(product_id)]['quantity'] = quantity
        
        request.session['cart'] = cart
        request.session.modified = True
        
        return redirect('view_cart')
    
    return redirect('view_cart')

def remove_from_cart(request, product_id):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        
        if str(product_id) in cart:
            del cart[str(product_id)]
        
        request.session['cart'] = cart
        request.session.modified = True
        
        return redirect('view_cart')
    
    return redirect('view_cart')

@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    
    if not cart:
        messages.error(request, "Your cart is empty!")
        return redirect('menu')
    
    cart_items = []
    total_price = 0
    
    for product_id, item in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            item_total = product.price * item['quantity']
            cart_items.append({
                'product': product,
                'quantity': item['quantity'],
                'total': item_total
            })
            total_price += item_total
        except Product.DoesNotExist:
            continue

    # Auto-fill form for logged in users
    initial_data = {}
    if request.user.is_authenticated:
        user = request.user
        initial_data = {
            'customer_name': f"{user.first_name} {user.last_name}".strip() or user.username,
            'customer_email': user.email,
            'customer_phone': user.phone,
            'customer_address': user.address,
        }

    if request.method == 'POST':
        form = OrderForm(request.POST, initial=initial_data)
        if form.is_valid():
            try:
                order = form.save(commit=False)
                order.total_amount = total_price
                order.user = request.user
                order.save()
                
                # Create order items
                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=item['product'],
                        quantity=item['quantity'],
                        price=item['product'].price
                    )
                
                # Clear the cart
                request.session['cart'] = {}
                request.session.modified = True
                
                messages.success(request, 'Order placed successfully!')
                return render(request, 'chocoberryapp/order_confirmation.html', {
                    'order': order
                })
            except Exception as e:
                messages.error(request, f"Error creating order: {str(e)}")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = OrderForm(initial=initial_data)
    
    return render(request, 'chocoberryapp/checkout.html', {
        'form': form,
        'cart_items': cart_items,
        'total_price': total_price
    })

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'chocoberryapp/order_history.html', {'orders': orders})