from django.test import TestCase

# Create your tests here.
from django.urls import reverse
from requests.auth import HTTPBasicAuth
from rest_framework import status
from rest_framework.test import APIClient, RequestsClient

from api.models import ClientUser, ProductCategory, Product


class TestClientLoginView(TestCase):

    def setUp(self) -> None:
        ClientUser.objects.create(
            consumer_key='pass',
            consumer_secret='pass'
        )
        self.client = RequestsClient()

    def test_can_login(self):
        self.client.auth = HTTPBasicAuth('pass', 'pass')
        self.client.headers.update({'x-test': 'true'})
        url = reverse('get_token')
        response = self.client.post('http://testserver{}'.format(url))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.json().get('access_token'))
        self.assertIsNotNone(response.json().get('expires_in'))

    def test_cannot_login_with_invalid_credentials(self):
        self.client.auth = HTTPBasicAuth('wrong', 'wrong')
        self.client.headers.update({'x-test': 'true'})
        url = reverse('get_token')
        response = self.client.post('http://testserver{}'.format(url))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIsNone(response.json().get('access_token'))
        self.assertIsNone(response.json().get('expires_in'))


class TestCreateCustomerApi(TestCase):
    def setUp(self) -> None:
        ClientUser.objects.create(
            consumer_key='pass',
            consumer_secret='pass'
        )
        self.client = RequestsClient()
        self.client.auth = HTTPBasicAuth('pass', 'pass')
        self.client.headers.update({'x-test': 'true'})
        url = reverse('get_token')
        response = self.client.post('http://testserver{}'.format(url))
        self.token = response.json().get('access_token')

    def test_can_create_user(self):
        client = RequestsClient()
        url = reverse('register')
        client.headers.update({'Authorization': 'Bearer {}'.format(self.token)})
        response = client.post('http://testserver{}'.format(url),
                               json={'msisdn': 254763488092, 'pin': 1212})
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_fails_if_token_is_wrong(self):
        client = RequestsClient()
        url = reverse('register')
        client.headers.update({'Authorization': 'Bearer {}'.format(self.token + 'extra')})
        response = client.post('http://testserver{}'.format(url),
                               json={'msisdn': 254763488092, 'pin': 1212})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_fails_if_msisdn_is_missing(self):
        client = RequestsClient()
        url = reverse('register')
        client.headers.update({'Authorization': 'Bearer {}'.format(self.token)})
        response = client.post('http://testserver{}'.format(url),
                               json={'pin': 1212})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_fails_if_pin_is_missing(self):
        client = RequestsClient()
        url = reverse('register')
        client.headers.update({'Authorization': 'Bearer {}'.format(self.token)})
        response = client.post('http://testserver{}'.format(url),
                               json={'msisdn': 254763488092})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_fails_if_pin_is_not_comprised_of_numbers(self):
        client = RequestsClient()
        url = reverse('register')
        client.headers.update({'Authorization': 'Bearer {}'.format(self.token)})
        response = client.post('http://testserver{}'.format(url),
                               json={'msisdn': 254763488092, 'pin': 'XXXX'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestCanLogin(TestCase):

    def setUp(self) -> None:
        ClientUser.objects.create(
            consumer_key='pass',
            consumer_secret='pass'
        )
        self.client = RequestsClient()
        self.client.auth = HTTPBasicAuth('pass', 'pass')
        self.client.headers.update({'x-test': 'true'})
        url = reverse('get_token')
        response = self.client.post('http://testserver{}'.format(url))
        self.token = response.json().get('access_token')
        self.client = RequestsClient()
        self.client.headers.update({'Authorization': 'Bearer {}'.format(self.token)})
        url = reverse('register')
        self.client.post('http://testserver{}'.format(url),
                         json={'msisdn': 254763488092, 'pin': 1212})

    def test_can_login(self):
        client = RequestsClient()
        url = reverse('login')
        client.headers.update({'Authorization': 'Bearer {}'.format(self.token)})
        response = client.post('http://testserver{}'.format(url),
                               json={'msisdn': 254763488092, 'pin': 1212})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestCanAddProduct(TestCase):

    def setUp(self) -> None:
        ClientUser.objects.create(
            consumer_key='pass',
            consumer_secret='pass'
        )
        self.client = RequestsClient()
        self.client.auth = HTTPBasicAuth('pass', 'pass')
        self.client.headers.update({'x-test': 'true'})
        url = reverse('get_token')
        response = self.client.post('http://testserver{}'.format(url))
        self.token = response.json().get('access_token')
        self.client = RequestsClient()
        self.client.headers.update({'Authorization': 'Bearer {}'.format(self.token)})
        url = reverse('register')
        self.client.post('http://testserver{}'.format(url),
                         json={'msisdn': 254763488092, 'pin': 1212})
        category = ProductCategory.objects.create(name='Category')
        url = reverse('login')
        self.client.headers.update({'Authorization': 'Bearer {}'.format(self.token)})
        response = self.client.post('http://testserver{}'.format(url),
                               json={'msisdn': 254763488092, 'pin': 1212})
        self.client.headers.update({'X-SESSION-KEY': response.json().get('session_key')})
        Product.objects.create(
            name='Jeans',
            price=100.00,
            category=category
        )

    def test_can_add_product(self):
        url = reverse('add-product')
        response = self.client.post('http://testserver{}'.format(url),
                         json={'product_id': 1})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
