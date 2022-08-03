from django.contrib import admin
from .models import Category ,Account, UserProfile
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
# Register your models here.


class CategoryAdmin(admin.ModelAdmin):
    list_display=('category_name','slug','description','Cat_image')
    list_display_links=('category_name','slug',)
    prepopulated_fields={'slug':('category_name',)}
    
admin.site.register(Category,CategoryAdmin)

      


class AccountAdmin(UserAdmin):
    list_display=('email','first_name','last_name', 'username','last_login','date_joined','is_active',)
    list_display_links=('email','first_name','last_name')
    readonly_fields=('last_login','date_joined')
    ordering=('-date_joined',)

    
    #since we are using custom user model so we have to wite following codes
    filter_horizontal=()
    list_filter=('date_joined','is_active')

    fieldsets=() #make password read only
admin.site.register(Account, AccountAdmin)

class UserProfileAdmin(admin.ModelAdmin):
    def thumbnail(self,object):
        return format_html('<img src="{}" width="30" style="border-radius:50%;">'.format(object.profile_picture.url))
    thumbnail.short_description = 'Profile Picture'
    list_display=('thumbnail','user','city','state', 'country')
    
admin.site.register(UserProfile, UserProfileAdmin)

      