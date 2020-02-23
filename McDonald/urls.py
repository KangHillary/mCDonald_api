"""McDonald URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.contrib.sessions.models import Session
from django.urls import path
from django.conf.urls.static import static
from api.views import ClientLoginView, CreateCustomerApi, CustomerLoginApi, AddProductToCart, RemoveProductFromCart, \
    ListAllProductsInCart, ConfirmOrderApi, CategoryApiView, ProductModelSetView
from simulator.views import UssdSimulatorView
from ussd.views import USSDGateWayOukitel

urlpatterns = [
    path('admin/', admin.site.urls),
    path('v1/ussd/request_access_token/', ClientLoginView.as_view(), name='get_token'),
    path('v1/ussd/register/', CreateCustomerApi.as_view(), name='register'),
    path('v1/ussd/login/', CustomerLoginApi.as_view(), name='login'),
    path('v1/ussd/cart/add/', AddProductToCart.as_view(), name='add-product'),
    path('v1/ussd/cart/remove/', RemoveProductFromCart.as_view(), name='remove-product'),
    path('v1/ussd/cart/items/', ListAllProductsInCart.as_view()),
    path('v1/ussd/cart/checkout/', ConfirmOrderApi.as_view()),
    path('v1/ussd/product_categories/', CategoryApiView.as_view()),
    path('v1/ussd/product/', ProductModelSetView.as_view()),
    path('v1/ussd/mc_donald/', USSDGateWayOukitel.as_view(), name='gateway'),
    path('v1/ussd/simulator/', UssdSimulatorView.as_view(), name='simulator')
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)