from django.shortcuts import render, redirect
from .models import Product, Location
from .forms import ContactForm
from django.db.models import Q

def home(request):
    featured_products = Product.objects.filter(is_popular=True)[:4] or Product.objects.all()[:4]
    return render(request, 'chocoberryapp/home.html', {'featured_products': featured_products})

def menu(request):
    query = request.GET.get('q')
    products = Product.objects.all()
    
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(category__icontains=query)
        )
    
    categories = Product.objects.values_list('category', flat=True).distinct()
    return render(request, 'chocoberryapp/menu.html', {
        'products': products, 
        'categories': categories,
        'search_query': query
    })

def locations(request):
    locations = Location.objects.all()
    # If no locations exist, the template will show default locations
    return render(request, 'chocoberryapp/locations.html', {'locations': locations})

def about(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            # Add success message
            return render(request, 'chocoberryapp/about.html', {
                'form': ContactForm(),
                'success_message': 'Thank you for your message! We will contact you soon.'
            })
    else:
        form = ContactForm()
    
    return render(request, 'chocoberryapp/about.html', {'form': form})