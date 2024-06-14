# Register your models here.
from django.contrib import admin
from .models import Category, Order, OrderItem, MenuItem
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

class UserAdmin(BaseUserAdmin):
    # Customize the admin options here if necessary
    pass

admin.site.register(Category)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(MenuItem)
admin.site.register(User, UserAdmin)