from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib import messages, auth
from .models import Product, ReviewRating, ProductGallery
from orders.models import OrderProduct
from eapp.models import Category
from cart.models import Cart_item
from cart.views import _cart_id
from .forms import ReviewRatingForm
from django.http import HttpResponse
from eapp.models import Account, UserProfile

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
# Create your views here.

def store(request,category_slug=None):
    categories  = None
    products    = None

    if category_slug != None :
        categories  = get_object_or_404(Category, slug=category_slug)
        products    = Product.objects.filter(category=categories,is_available=True)


    else:
        products    = Product.objects.all().filter(is_available=True)
    
    for product in products:
        reviews = ReviewRating.objects.filter(product_id=product.id, status=True)

    paginator   = Paginator(products,6)
    page        = request.GET.get("page")
    paged_products = paginator.get_page(page)
    
    product_count = products.count()
    context = {
        "products"      : paged_products,
        "product_count" : product_count,
        "reviews"       : reviews
    }
    return render(request, 'store/store.html', context)


def product_detail(request, category_slug, product_slug):
    try:
        single_product  = Product.objects.get(category__slug=category_slug,slug=product_slug)
        in_cart         = Cart_item.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()


    except Exception as e:
        raise e

    if request.user.is_authenticated:
        try :
            orderproduct = OrderProduct.objects.filter(user=request.user,product_id=single_product.id).exists()
        except orderproduct.DoesNotExist:
            orderproduct = False
    else:
        orderproduct = False
    


    # get the reviews
    reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)
    user = request.user
    userlog = user.is_authenticated
    if userlog :
        # userprofile = get_object_or_404(UserProfile, user = user)
        try:
            userprofile = UserProfile.objects.get(user_id = user.id)
        except:
            userprofile = None
    else :
        userprofile = None


    # get the product gallery
    product_gallery = ProductGallery.objects.filter(product_id=single_product.id)

    context ={
        'single_product'    :single_product,
        'in_cart'           :in_cart,
        'orderproduct'      :orderproduct,
        'reviews'           :reviews,
        'product_gallery'   :product_gallery,
        # 'userprofile'       :userprofile,
        }

    return render(request,"store/product_detail.html",context)

def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            products    = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
    product_count   = products.count()

    context={
        "products"      :   products,
        "product_count" :   product_count
    }

    return render(request,"store/store.html",context)


def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    user = request.user
    if request.method == 'POST':
        try: 
            review = ReviewRating.objects.get(user__id=user.id,product__id=product_id)
            form = ReviewRatingForm(request.POST, instance=review)
            form.save()
            messages.success(request,'Thank you. Your review has been updated.')
            
        
        except ReviewRating.DoesNotExist:
            form = ReviewRatingForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.review = form.cleaned_data['review']
                data.rating = form.cleaned_data['rating']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Thank you. Your review has been submitted. ')
    return redirect(url)
