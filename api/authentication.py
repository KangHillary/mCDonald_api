import base64
import binascii
from datetime import timedelta

from annoying.functions import get_object_or_None
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import HTTP_HEADER_ENCODING
from rest_framework.authentication import TokenAuthentication, get_authorization_header
from rest_framework.authtoken.models import Token
# this return left time
from rest_framework.exceptions import PermissionDenied, AuthenticationFailed

from api.models import ClientUser


def expires_in(token):
    time_elapsed = timezone.now() - token.created
    left_time = timedelta(seconds=settings.TOKEN_EXPIRED_AFTER_SECONDS) - time_elapsed
    return left_time


# token checker if token expired or not
def is_token_expired(token):
    return expires_in(token) < timedelta(seconds=0)


# if token is expired new token will be established
# If token is expired then it will be removed
# and new one with different key will be created
def token_expire_handler(token):
    is_expired = is_token_expired(token)
    if is_expired:
        token.delete()
        token = Token.objects.create(user=token.user)
    return is_expired, token


def authenticate(request):
    """
    Returns a `User` if a correct consumer key and consumer secret have been supplied
    using HTTP Basic authentication.  Otherwise returns `None`.
    """
    auth = get_authorization_header(request).split()

    if not auth or auth[0].lower() != b'basic':
        return None

    if len(auth) == 1:
        msg = _('Invalid basic header. No credentials provided.')
        raise AuthenticationFailed(msg)
    elif len(auth) > 2:
        msg = _('Invalid basic header. Credentials string should not contain spaces.')
        raise AuthenticationFailed(msg)

    try:
        auth_parts = base64.b64decode(auth[1]).decode(HTTP_HEADER_ENCODING).partition(':')
    except (TypeError, UnicodeDecodeError, binascii.Error):
        msg = _('Invalid basic header. Credentials not correctly base64 encoded.')
        raise AuthenticationFailed(msg)

    consumer_key, consumer_secret = auth_parts[0], auth_parts[2]
    user = get_object_or_None(ClientUser, consumer_key=consumer_key, consumer_secret=consumer_secret)
    if user is None:
        raise AuthenticationFailed(_('Invalid consumer_key/consumer_password.'))

    if not user.is_active:
        raise AuthenticationFailed(_('User inactive or deleted.'))
    return user


# DEFAULT_AUTHENTICATION_CLASSES
class ExpiringTokenAuthentication(TokenAuthentication):

    keyword = 'Bearer'

    def authenticate_credentials(self, key):
        try:
            token = Token.objects.get(key=key)
        except Token.DoesNotExist:
            raise AuthenticationFailed("Invalid Token")

        if not token.user.is_active:
            raise AuthenticationFailed("User is not active")

        is_expired, token = token_expire_handler(token)
        if is_expired:
            raise AuthenticationFailed("The Token is expired")

        return token.user, token
