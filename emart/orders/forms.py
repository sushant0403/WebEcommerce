from django import forms
from .models import Order

class Orderform(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name','last_name','email','phone_number','address1','address2','country','state','city','order_note']