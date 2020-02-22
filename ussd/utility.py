from requests.auth import HTTPBasicAuth
from ussdframework.core import register_function


@register_function
def auth_header(username, password):
    return HTTPBasicAuth(username, password)


@register_function
def auth_token(token):
    return 'Bearer {}'.format(token)