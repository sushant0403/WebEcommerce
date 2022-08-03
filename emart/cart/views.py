from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Variation
from .models import Cart, Cart_item
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
# import requests
# Create your views here.

def _cart_id(request):
    cart    = request.session.session_key
    if not cart:
        cart    = request.session.create()
    return cart

def add_cart(request, product_id):

    product             = Product.objects.get(id=product_id)
    if request.user.is_authenticated:
        curent_user     = request.user
        product_variation   = []
        if request.method   =='POST':
            for item in request.POST:
                key = item 
                value = request.POST[key]

                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass

        is_cart_item_exists = Cart_item.objects.filter(product=product, user=curent_user).exists()

        if is_cart_item_exists:
            cart_item   = Cart_item.objects.filter(product=product,user=curent_user)

            ex_var_list =[]
            id_list =[]

            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id_list.append(item.id)


            if product_variation in ex_var_list:
                index = ex_var_list.index(product_variation)
                item_id = id_list[index]
                cart_item = Cart_item.objects.get(product=product, user = curent_user, id=item_id) 
                cart_item.quantity  +=  1
            else: 
                cart_item = Cart_item.objects.create(product= product,user= curent_user,quantity= 1)
                if len(product_variation) > 0:
                    cart_item.variations.clear()
                    cart_item.variations.add(*product_variation) 

        else:
            cart_item = Cart_item.objects.create(product= product,user= curent_user,quantity= 1)
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation) 
        cart_item.save()

        return redirect('cart')


    else:
        product_variation   = []
        if request.method   =='POST':
            for item in request.POST:
                key = item 
                value = request.POST[key]

                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass



        try:
            cart = Cart.objects.get(cart_id=_cart_id(request)) 

        except Cart.DoesNotExist:
            cart    =   Cart.objects.create(
                cart_id=_cart_id(request)
            )
        cart.save()

        is_cart_item_exists = Cart_item.objects.filter(product=product, cart=cart).exists()

        if is_cart_item_exists:
            cart_item   = Cart_item.objects.filter(product=product,cart=cart)

            ex_var_list =[]
            id_list =[]

            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id_list.append(item.id)


            if product_variation in ex_var_list:
                index = ex_var_list.index(product_variation)
                item_id = id_list[index]
                cart_item = Cart_item.objects.get(product=product, cart = cart, id=item_id) 
                cart_item.quantity  +=  1
            else: 
                cart_item = Cart_item.objects.create(product= product,cart= cart,quantity= 1)
                if len(product_variation) > 0:
                    cart_item.variations.clear()
                    cart_item.variations.add(*product_variation) 

        else:
            cart_item = Cart_item.objects.create(product= product,cart= cart,quantity= 1)
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation) 
        cart_item.save()

        return redirect('cart')



def sub_cart(request, product_id, cart_item_id):
    product     =   get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item  =   Cart_item.objects.get(user=request.user, product=product , id=cart_item_id)
        else:
            cart        =   Cart.objects.get(cart_id=_cart_id(request))
            cart_item  =   Cart_item.objects.get(cart=cart, product=product , id=cart_item_id)

        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')



def remove_cart(request, product_id , cart_item_id):
    product     =   get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item  =   Cart_item.objects.get(user=request.user, product=product, id= cart_item_id)
    else:
        cart        =   Cart.objects.get(cart_id=_cart_id(request))
        cart_item  =   Cart_item.objects.get(cart=cart, product=product, id= cart_item_id)
    
    cart_item.delete() 
    return redirect('cart')

def cart(request, total=0, quantity=0, cart_items = None):
    try :
        if request.user.is_authenticated :
            cart_items  =   Cart_item.objects.all().filter(user=request.user, is_active=True)
        else:
            cart        =   Cart.objects.get(cart_id=_cart_id(request))
            cart_items  =   Cart_item.objects.filter(cart=cart, is_active=True)
        cart_item_count = cart_items.count()

        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2*total)/100
        grand_total = total + tax

        context     ={
            "total"                 :  total,
            "tax"                   :  tax,
            "grand_total"           :  grand_total,
            "quantity"              :  quantity,
            "cart_items"            :  cart_items,
            "cart_item_count"       :  cart_item_count
        }
    except ObjectDoesNotExist:
        context={}
        pass # ignore
        

    return render(request,'cart/cart.html' , context)



@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_items = None):
    try :
        if request.user.is_authenticated :
            cart_items  =   Cart_item.objects.all().filter(user=request.user, is_active=True)
        else:
            cart        =   Cart.objects.get(cart_id=_cart_id(request))
            cart_items  =   Cart_item.objects.filter(cart=cart, is_active=True)
        cart_item_count = cart_items.count()

        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2*total)/100
        grand_total = total + tax

        context     ={
            "total"                 :  total,
            "tax"                   :  tax,
            "grand_total"           :  grand_total,
            "quantity"              :  quantity,
            "cart_items"            :  cart_items,
            "cart_item_count"       :  cart_item_count
        }
    except ObjectDoesNotExist:
        context={}
        pass # ignore
        

    return render(request,'cart/checkout.html' , context)
