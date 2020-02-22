# Create your views here.
import uuid

from annoying.functions import get_object_or_None
from rest_framework.authentication import get_authorization_header
from rest_framework.authtoken.models import Token
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_401_UNAUTHORIZED, HTTP_202_ACCEPTED
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework import generics

from api.authentication import token_expire_handler, expires_in, authenticate, ExpiringTokenAuthentication
from api.models import Customer, SessionKey, Product, Cart, Order, ProductCategory
from api.serializer import CustomerSerializer, CustomerLoginSerializer, ProductSerializer, ProductCategorySerializer, \
    ProductModelSerializer


class ClientLoginView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        auth = get_authorization_header(request).split()

        user = authenticate(
            request=request
        )

        # TOKEN STUFF
        token, _ = Token.objects.get_or_create(user=user)

        # token_expire_handler will check, if the token is expired it will generate new one
        is_expired, token = token_expire_handler(token)  # The implementation will be described further

        return Response({
            'expires_in': expires_in(token),
            'access_token': token.key
        }, status=HTTP_200_OK)


class CreateCustomerApi(CreateAPIView):
    serializer_class = CustomerSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(status=HTTP_202_ACCEPTED, headers=headers)


class CustomerLoginApi(APIView):

    def post(self, request):
        serializer = CustomerLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.perform_login(serializer=serializer)

    def perform_login(self, serializer):
        customer = get_object_or_None(Customer, **serializer.data)
        if customer:
            return self.create_session(customer=customer)
        return Response(status=HTTP_401_UNAUTHORIZED)

    def create_session(self, customer):
        session_key = SessionKey.objects.create(customer=customer, session_key=str(uuid.uuid4()))
        return Response(data=self.get_response_payload(session_key=session_key),
                        status=HTTP_200_OK)

    @staticmethod
    def get_response_payload(session_key: SessionKey):
        return {
            "expire_in": session_key.remaining_time_to_expire(),
            "session_key": session_key.session_key
        }


class AddProductToCart(APIView):
    session_key = ''

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session_key = request.META.get('HTTP_X_SESSION_KEY', b'')
        try:
            self.session_key = SessionKey.objects.get(session_key=session_key)
        except SessionKey.DoesNotExist:
            raise session_key.DoesNotExist
        return Response(status=HTTP_201_CREATED, data=self.perform_add_product(serializer=serializer))

    def perform_add_product(self, serializer):
        product = get_object_or_None(Product, id=serializer.data.get('product_id'))
        cart, _ = Cart.objects.get_or_create(session_key=self.session_key)
        cart.add_product(product)
        return self.get_response_payload(serializer=serializer)

    def get_response_payload(self, serializer):
        return {
            'session_key': self.session_key.session_key,
            'product_id': serializer.data.get('product_id')
        }


class RemoveProductFromCart(APIView):
    session_key = ''

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session_key = request.META.get('HTTP_X_SESSION_KEY', b'')
        try:
            self.session_key = SessionKey.objects.get(session_key=session_key)
        except SessionKey.DoesNotExist:
            raise session_key.DoesNotExist
        return Response(status=HTTP_200_OK, data=self.perform_remove_product(serializer=serializer))

    def perform_remove_product(self, serializer):
        product = get_object_or_None(Product, id=serializer.data.get('product_id'))
        cart = Cart.objects.get(session_key=self.session_key)
        cart.remove_product(product)
        return self.get_response_payload(serializer=serializer)

    def get_response_payload(self, serializer):
        return {
            'session_key': self.session_key.session_key,
            'product_id': serializer.data.get('product_id')
        }


class ListAllProductsInCart(APIView):

    def get(self, request):
        session_key = request.META.get('HTTP_X_SESSION_KEY', b'')
        try:
            cart = Cart.objects.get(session_key__session_key=session_key)
        except Cart.DoesNotExist:
            raise Cart.DoesNotExist
        return Response(status=HTTP_200_OK, data=self.get_response_payload(cart=cart))

    @staticmethod
    def get_response_payload(cart: Cart):
        return ["{}X {} (KSH{})".format(1, product.name, product.price) for product in cart.products.all()]


class ConfirmOrderApi(APIView):

    def get(self, request):
        session_key = request.META.get('HTTP_X_SESSION_KEY', b'')
        try:
            cart = Cart.objects.get(session_key__session_key=session_key)
        except Cart.DoesNotExist:
            raise Cart.DoesNotExist
        order = self.perform_create_order(cart=cart)
        return Response(status=HTTP_200_OK, data=self.get_response_payload(order=order))

    @staticmethod
    def perform_create_order(cart):
        return Order.objects.create(
            cart=cart,
            total_cost=cart.calculate_total_cost_of_cart()
        )

    @staticmethod
    def get_response_payload(order):
        return {
            "message": "Order placed successfully. Total KES{}."
                       " Expected time of delivery is {} minutes".format(order.total_cost,
                                                                         order.estimated_delivery_time_in_minutes)
        }


class CategoryApiView(generics.ListAPIView):
    serializer_class = ProductCategorySerializer
    queryset = ProductCategory.objects.all()


class ProductModelSetView(generics.RetrieveAPIView):
    serializer_class = ProductModelSerializer
    queryset = Product.objects.all()

