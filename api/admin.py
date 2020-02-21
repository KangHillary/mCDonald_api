from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import ClientUser, Product, ProductCategory, Cart, Order, Customer


class CustomUserAdmin(UserAdmin):
    fieldsets = (
        *UserAdmin.fieldsets,  # original form fieldsets, expanded
        (  # new fieldset added on to the bottom
            'Client Login',  # group heading of your choice; set to None for a blank space instead of a header
            {
                'fields': (
                    'consumer_key',
                    'consumer_secret'
                ),
            },
        ),
    )


class ProductAdmin(admin.ModelAdmin):
    fields = ('name', 'price', 'category')


class ProductCategoryAdmin(admin.ModelAdmin):
    fields = ('name',)


class CartAdmin(admin.ModelAdmin):
    fields = ('session_key','products')


class OrderAdmin(admin.ModelAdmin):
    fields = ('total_cost', 'cart', 'estimated_delivery_time_in_minutes', 'is_delivered')


class CustomerAdmin(admin.ModelAdmin):
    fields = ('msisdn', 'pin')


admin.site.register(ClientUser, CustomUserAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductCategory, ProductCategoryAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Customer, CustomerAdmin)
