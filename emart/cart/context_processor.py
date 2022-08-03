from .models import Cart, Cart_item
from .views import _cart_id

def menu_links(request):
    try:
        if request.user.is_authenticated :
            cart_items  =   Cart_item.objects.all().filter(user=request.user)
        else:
            cart        =   Cart.objects.get(cart_id=_cart_id(request))
            cart_items  =   Cart_item.objects.all().filter(cart=cart)


    except:
        cart = 0
        cart_items  =   Cart_item.objects.filter(cart=cart, is_active=True)

    cart_item_count = cart_items.count()

    return dict( cart_item_count= cart_item_count)