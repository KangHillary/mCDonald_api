from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta

# Create your models here.


class ClientUser(AbstractUser):
    consumer_key = models.CharField(_('consumer_key'), max_length=40, unique=True)
    consumer_secret = models.CharField(_('consumer_secret'), max_length=128)


class Customer(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    msisdn = models.IntegerField(unique=True)
    pin = models.IntegerField()

    def __str__(self):
        return self.msisdn


class SessionKey(models.Model):
    session_key = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    expired = models.BooleanField(default=False)
    customer = models.ForeignKey(Customer, on_delete=models.DO_NOTHING)

    def remaining_time_to_expire(self):
        time_elapsed = timezone.now() - self.created_at
        left_time = timedelta(seconds=settings.SESSION_EXPIRED_AFTER_SECONDS) - time_elapsed
        if left_time <= timedelta(seconds=0):
            self.expired = True
            self.save()
        return left_time

    def __str__(self):
        return self.session_key


class ProductCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(ProductCategory, on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Cart(models.Model):
    session_key = models.OneToOneField(SessionKey, on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(auto_now_add=True)
    products = models.ManyToManyField(Product)

    def add_product(self, product):
        self.products.add(product)
        self.save()

    def remove_product(self, product):
        self.products.remove(product)
        self.save()

    def calculate_total_cost_of_cart(self):
        cost = 0.0
        for product in self.products.all():
            cost += float(product.price)
        return cost


class Order(models.Model):
    cart = models.OneToOneField(Cart, on_delete=models.DO_NOTHING)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_delivery_time_in_minutes = models.IntegerField(default=45)
    is_delivered = models.BooleanField(default=False)