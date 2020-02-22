import re

from annoying.functions import get_object_or_None
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.models import Customer, Product, ProductCategory


class CustomerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Customer
        fields = '__all__'


class ProductCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductCategory
        fields = '__all__'


class ProductModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = '__all__'


class CustomerLoginSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    pin = serializers.CharField(max_length=4)
    msisdn = serializers.CharField(max_length=100)

    def is_valid(self, raise_exception=False):
        pin = self.initial_data.get('pin')
        is_alphanumeric = str(pin).isnumeric()
        four_digits = len(str(pin)) == 4
        if not is_alphanumeric and four_digits:
            error = {"Invalid PIN": "PIN has incorrect syntax"}
            raise ValidationError(error)
        return super().is_valid(raise_exception)


class ProductSerializer(serializers.Serializer):
    product_id = serializers.CharField(max_length=100)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    def is_valid(self, raise_exception=False):
        product = get_object_or_None(Product, id=self.initial_data.get('product_id'))
        if not product:
            error = {"product_id": "{} Product does not exist".format(self.product_id)}
            raise ValidationError(error)
        return super().is_valid(raise_exception)