from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, User, PermissionsMixin, AbstractUser
from django.urls import reverse

# Create your models here.

class Category(models.Model):
    category_name       =   models.CharField(max_length=50, unique=True)
    slug                =   models.SlugField(max_length=100, unique=True)
    description         =   models.TextField(max_length=255, blank=True)
    Cat_image           =   models.ImageField(upload_to='static/images', blank=True)

    #to fix the pural form for categories into category in admin pannel
    class Meta:
        verbose_name        =   'category'
        verbose_name_plural =   'categories'
    
    def get_url(self):
        return reverse('products_by_categories',args=[self.slug])

        # verbose A human-readable name for the field.
        #  If the verbose name isn’t given,
        #  Django will automatically create it using the field’s attribute name,
        #  converting underscores to spaces.
    
    #string representation of model
    def __str__(self):
        return self.category_name

# model for custome user 
#to create account model



class MyAccountManager(BaseUserManager):
    
    def create_user(self,first_name, last_name, username, email, password=None):
        if not email:
            raise ValueError('User must have an emailaddress')
        if not username:
            raise ValueError('user must have an username')
        
        user=self.model(
            email       =   self.normalize_email(email), # if you enter capital emailaddress it will make small letter email automatically
            username    =   username,
            first_name  =   first_name,
            last_name   =   last_name,

        )

        user.set_password(password) #to set password
        user.save(using=self._db)
        return user



    def create_superuser(self, first_name, last_name, email, username, password):
        user=self.create_user(
            email       =   self.normalize_email(email),
            username    =   username,
            password    =   password,
            first_name  =   first_name,
            last_name   =   last_name,


            )

        user.is_admin       =   True
        user.is_active      =   True
        user.is_staff       =   True
        user.is_superadmin  =   True 
        user.save(using=self._db)
        return user
#model for superadmin





class Account(AbstractBaseUser):
    first_name      =   models.CharField(max_length=50)
    last_name       =   models.CharField(max_length=50)
    username        =   models.CharField(max_length=50, unique=True)
    email           =   models.EmailField(max_length=100, unique=True)
    phone_number    =   models.CharField(max_length=50)


    #required field for custom user model (madatory for custom user model)

    date_joined     =   models.DateTimeField(auto_now_add=True)
    last_login      =   models.DateTimeField(auto_now_add=True)
    is_admin        =   models.BooleanField(default=False)
    is_staff        =   models.BooleanField(default=False)
    is_active       =   models.BooleanField(default=False)
    is_superadmin   =   models.BooleanField(default=False)

    #to login as emailaddress
    USERNAME_FIELD      ='email'
    REQUIRED_FIELDS     =['username','first_name','last_name']

    objects         = MyAccountManager()

    def __str__(self):
        return self.email

    # must mention permision when we are building custom user model
    def has_perm(self, perm, obj=None):
        return self.is_admin  #if user is admin then he have all permission to do all changes  

    def has_module_perms(self, add_label):
        return True




class UserProfile(models.Model):
    user            = models.OneToOneField(Account, on_delete=models.CASCADE)
    address1        = models.CharField(blank =True, max_length=100)
    address2        = models.CharField(blank =True, max_length=100)
    profile_picture = models.ImageField(upload_to='static/images/userprofile', blank =True)
    city            = models.CharField(blank =True, max_length=20)
    state           = models.CharField(blank =True, max_length=20)
    country         = models.CharField(blank =True, max_length=20)

    def __str__(self):
        return self.user.first_name


    def full_address(self):
        return f'{self.address1}, {self.address2}'

