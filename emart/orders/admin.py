from django.contrib import admin
from .models import Payment, Order, OrderProduct
# Register your models here.

class OrderProductInline(admin.TabularInline):
    model           = OrderProduct
    readonly_fields = ['order','user','payment','product','ordered','variations','product_price','quantity']
    extra           = 0 

class OrderAdmin(admin.ModelAdmin):
    list_display    = ['order_number','email','first_name','is_ordered','status']
    list_filter     = ['status','is_ordered']
    search_fields   = ['order_number','email','first_name']
    list_per_page   = 20
    inlines         = [OrderProductInline]

# registration in admin site
admin.site.register(Payment)
admin.site.register(Order,OrderAdmin)
admin.site.register(OrderProduct)