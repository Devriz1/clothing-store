from django.shortcuts import render
from .models import Product
from django.shortcuts import get_object_or_404
from .models import Category
from django.db.models import Min



def home(request):
    products = Product.objects.prefetch_related('variants').all()

    for product in products:
        lowest = product.variants.aggregate(Min('price'))['price__min']
        product.display_price = lowest

    return render(request, 'store/home.html', {
        'products': products
    })

def product_detail(request, slug):
    product = Product.objects.get(slug=slug)

    colors = product.variants.values_list('color', flat=True).distinct()
    sizes = product.variants.values_list('size', flat=True).distinct()

    related_products = Product.objects.filter(
        category=product.category
    ).exclude(id=product.id)[:4]

    context = {
        'product': product,
        'colors': colors,
        'sizes': sizes,
        'related_products': related_products
    }

    return render(request, 'store/product_detail.html', context)
def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = category.products.all()
    return render(request, 'store/category.html', {
        'category': category,
        'products': products
    })

def privacy_policy(request):
    return render(request, "store/privacy_policy.html")

def terms_conditions(request):
    return render(request, "store/terms_conditions.html")
def contact(request):
    return render(request, "store/contact.html")