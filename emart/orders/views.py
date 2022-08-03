from django.shortcuts import render, redirect, get_object_or_404
from .models import Order, Payment, OrderProduct
from cart.models import Cart_item
from store.models import Product
from .forms import Orderform
import datetime
from django.http import HttpResponse
from django.core.mail import EmailMessage, send_mail
from django.template.loader import render_to_string
# Create your views here.

def payments(request, order_number, total):
    current_user    = request.user
    tax             = total*2/100
    # bring payment info
    order       = Order.objects.get(order_number=order_number,user = current_user)
    cart_items  = Cart_item.objects.filter(user=current_user)
    payment     = Payment(
        user            = current_user,
        payment_id      = order.order_number,
        payment_method  = "paypal",
        amount_paid     = order.order_total,
        status          = 'completed'
    )
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()
    # move the cart items to order product table
    for item in cart_items:
        orderproduct            = OrderProduct()
        orderproduct.order_id   = order.id
        orderproduct.payment    = payment
        orderproduct.user_id    = request.user.id
        orderproduct.product_id = item.product.id
        orderproduct.quantity   = item.quantity
        price                   = item.quantity*item.product.price
        orderproduct.product_price = price
        orderproduct.ordered    = True
        orderproduct.save()

        cart_item               = Cart_item.objects.get(id=item.id)
        product_variation       = cart_item.variations.all()
        orderproduct            = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variations.set(product_variation)
        orderproduct.save()

        # reduce the quantity of sold products
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()

    # clear the cart
    Cart_item.objects.filter(user=current_user).delete()

    # send order reveived email to customer
    mail_subject = 'Thank You for Your order!'
    message = f"Hi {current_user.first_name}\nYOUR ORDER HAS BEEN RECEIVED.\nOrder Number : {order.order_number}\nThank you."
    to_email = current_user.email

    send_mail(
                mail_subject, 
                message, 
                'thakurisushant0403@gmail.com',
                [to_email], 
                fail_silently=False,
                )

    # send_email.send()
    # send transaction id back to site
    orderproducts = OrderProduct.objects.filter(order_id=order.id)
    context={
        'order':order,
        'payment':payment,
        'total':total,
        'tax':tax,
        'orderproducts':orderproducts,
    }

    return render(request, 'order/order_complete.html',context)



def place_order(request , total =0, quantity = 0):
    current_user = request.user
 
    cart_items = Cart_item.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0 :
        return redirect('store')
    print("works")
    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2*total)/100
    grand_total = total + tax
    print("works1")
    
    if request.method == 'POST':
        form = Orderform(request.POST)
        print(form)
        print("works2")

        if form.is_valid():
            data=Order()
            data.user = current_user
            data.first_name= form.cleaned_data['first_name']
            data.last_name= form.cleaned_data['last_name']
            data.email= form.cleaned_data['email']
            data.phone_number= form.cleaned_data['phone_number']
            data.address1= form.cleaned_data['address1']
            data.address2= form.cleaned_data['address2']
            data.city= form.cleaned_data['city']
            data.state= form.cleaned_data['state']
            data.country= form.cleaned_data['country']
            data.order_note= form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            print("works3")

            # generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            mt = int(datetime.date.today().strftime('%m'))
            dt = int(datetime.date.today().strftime('%d'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime('%Y%m%d')
            order_number = current_date+str(data.id)
            data.order_number = order_number
            data.save()
            print("works4")

            order = Order.objects.get(user = current_user, is_ordered=False,order_number= order_number)

            context={
                'quantity':quantity,
                'grand_total':grand_total,
                'total':total,
                'tax':tax,
                'order': order,
                'cart_items':cart_items,
            }
            return render(request,'order/payments.html', context)
    else:
        print("works5")

        return redirect('checkout')
