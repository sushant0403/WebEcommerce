from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistrationForm, UserForm, UserProfileForm
from eapp.models import Account, UserProfile
from orders.models import Order, OrderProduct, Payment
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate

# mail verification import

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode ,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage, send_mail

# cart item assignments
from cart.models import Cart, Cart_item
from cart.views import _cart_id
# import requests



# Create your views here.

def register(request):

    if request.method == 'POST':

        form = RegistrationForm(request.POST)

        if form.is_valid():

            first_name          = form.cleaned_data['first_name']
            last_name           = form.cleaned_data['last_name']
            phone_number        = form.cleaned_data['phone_number']
            email               = form.cleaned_data['email']
            password            = form.cleaned_data['password']
            username            = email.split("@")[0]
            user                = Account.objects.create_user(username=username,first_name=first_name, last_name=last_name, password=password,email=email)
            user.phone_number   = phone_number
            
            
            # verification email
            current_site  = get_current_site(request)
            mail_subject = 'Please activate your account'
            message = render_to_string('accounts/account_verification_email.html',{
                'user':user,
                'domain':current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            # send_email = EmailMessage(mail_subject, message, to=[to_email])

            send_mail(
                mail_subject, 
                message, 
                'thakurisushant0403@gmail.com',
                [to_email], 
                fail_silently=False,
                )
            # send_email.send()
            # message.success(request, 'Thank you for registering with us. We have sent you a verification mail to {{email}}. You need to verify to login with this account.')
            user.save()

            return redirect('/accounts/login/?command=verification&email='+email)


    else:

        form = RegistrationForm()

    context = {
        'form' :  form,
    }

    return render(request, "accounts/register.html",context)



def login(request):

    user = None

    if request.method=="POST":

        email = request.POST['email']
        password = request.POST['password']

        user = authenticate(email=email , password=password)
        if user is not None:
            try:
                cart= Cart.objects.get(cart_id=_cart_id(request))
                cart_item_exists= Cart_item.objects.filter(cart=cart).exists()
                product_variation=[]
                ex_var_list = []
                id = []
                if cart_item_exists:
                    cart_item = Cart_item.objects.filter(cart=cart)
                    # getting the product variation by cart id
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))
                    cart_item = Cart_item.objects.all().filter(user= user)
                    for item in cart_item:
                        existing_variation = item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)
                    for pr in product_variation:
                        if pr in ex_var_list:
                            index   = ex_var_list.index(pr)
                            item_id = id[index]
                            item = Cart_item.objects.get(id=item_id)
                            item.quantity +=1
                            item.user = user
                            item.save()
                        else :
                            cart_item = Cart_item.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()
            
            except:
                pass

            auth.login(request, user)
            messages.success(request,"login successful")
            url = request.META.get('HTTP_REFERER')
            # try:
            #     query = requests.utils.urlparse(url).query
            #     params = dict(x.split('=') for x in query.split('&')) 
            #     if 'next' in params:
            #         nextpage = params['next']
            #         return redirect(nextpage)
            # except:
            return redirect('dashboard')

        else:

            messages.error(request,"invalid credentials!")
            return redirect('login')
    return render(request, "accounts/login.html")

@login_required(login_url="login")
def logout(request):

    auth.logout(request)
    messages.success(request,"You are logged out.")

    return redirect('login')


def activate(request, uidb64, token):

    try:
        uid  = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)

    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):

        user.is_active  = True
        user.save()
        messages.success(request,'Congratulations your account is activated.')
        return redirect('login')

    else:

        messages.error(request,'Invalid activation link')
        return redirect('register')


@login_required(login_url="login")
def dashboard(request):
    user = request.user
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id,is_ordered=True)
    order_count = orders.count()
    try:
        userprofile = UserProfile.objects.get(user_id = user.id)
    except:
        userprofile = None
    context = {
        'orders': orders,
        'order_count':order_count,
        'userprofile':userprofile,
    }
    return render(request, "accounts/dashboard.html",context)


def forgotpassword(request):

    if request.method == 'POST':
        email = request.POST['email']

        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__iexact=email)

            # forgot password email
            current_site  = get_current_site(request)
            mail_subject = 'Reset password using the given link below:'
            message = render_to_string('accounts/reset_password_email.html',{
                'user':user,
                'domain':current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_mail(
                mail_subject, 
                message, 
                'thakurisushant0403@gmail.com',
                [to_email], 
                fail_silently=False,
                )

            # send_email = EmailMessage(mail_subject, message, to=[to_email])
            # send_email.send()
            return redirect('/accounts/login/?command=resetpassword&email='+email)
        
        else:
            messages.error(request,'The given email doesnot exists.')
            return redirect('forgotpassword')
    
    return render(request,"accounts/forgotpassword.html")


def resetpassword_validation(request, uidb64, token):

    try:
        uid  = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid']  =   uid
        messages.success(request,"please reset your password.")
        return redirect('resetpassword')

    else:
        messages.error(request,"Invalid link.")
        return redirect('login')



def resetpassword(request):

    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password :
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request,"Password reset successful.")
            return redirect('login')
        
        else:
            messages.error(request,"passwords don't match")
            # return redirect('resetpassword')
    
    return render(request,'accounts/resetpassword.html')

@login_required(login_url="login")
def change_password(request):
    if request.method == "POST":
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = Account.objects.get(username__exact=request.user.username)

        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                messages.success(request,"Password updated sucessfully.")
                return redirect('change_password')

            else:
                messages.error(request,"Please enter valid current password")
                return redirect('change_password')

        else:
            messages.error(request, "Password does not match")
            return redirect('change_password')
    
    return render(request, "accounts/change_password.html")


@login_required(login_url="login")
def my_orders(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id,is_ordered=True)
    context = {
        'orders': orders,
    }
    return render(request, "accounts/my_orders.html", context)


@login_required(login_url="login")
def edit_profile(request):
    user = request.user
    try:
        userprofile = UserProfile.objects.get(user_id = user.id)
    except:
        userprofile = None
    if request.method == "POST":
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST,request.FILES, instance=userprofile)
        if user_form.is_valid()and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has benn updated.')
    else :
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance= userprofile)
    context= {
        'user_form':user_form,
        'profile_form':profile_form,
        'userprofile':userprofile,
    }
    return render(request,"accounts/edit_profile.html",context)




def order_detail(request , order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number = order_id)
    total = 0
    for i in order_detail:
        total += i.product_price * i.quantity
    tax = total * 0.02
    context = {
        'order_detail':order_detail,
        'order':order,
        'total': total,
        'tax': tax,
    }
    return render(request, "accounts/order_detail.html", context)