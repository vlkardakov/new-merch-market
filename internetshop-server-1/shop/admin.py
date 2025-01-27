from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Product, Review, CustomUser


class ProductAdmin(admin.ModelAdmin):
    pass

class ReviewAdmin(admin.ModelAdmin):
    pass

from .models import CustomUser

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'balance', 'is_active','is_staff', 'is_superuser','first_name','last_name')
    fields = ('username', 'email', 'balance', 'is_active','is_staff', 'is_superuser','first_name','last_name')

admin.site.register(CustomUser, CustomUserAdmin)

# Register your models here.
admin.site.register(Product, ProductAdmin)
admin.site.register(Review, ReviewAdmin)