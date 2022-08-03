from django.shortcuts import render
from store.models import Product, ReviewRating
from .models import Category
# Create your views here.

def index(request):
    reviews = None
    topProducts = []
    products = Product.objects.all().filter(is_available=True)
    recomendedproducts = Product.objects.all().filter(is_available=True)[::-1]
    categories = Category.objects.all()
    
    for product in products:
        reviews = ReviewRating.objects.filter(product_id=product.id, status=True)
        # print(product.averagereview())
        if product.averagereview() >= 4:
            topProducts.append(Product.objects.get(id=product.id))
    context = {
        "products"              : products,
        "categories"            : categories,
        'reviews'               : reviews,
        "topProducts"           : topProducts[::-1],
        "recomendedproducts"    : recomendedproducts,
    }
    return render(request, 'index.html', context)
