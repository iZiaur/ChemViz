from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from equipment_api.models import Token


class TokenAuthentication(BaseAuthentication):
    """
    Custom Token authentication.
    Clients should authenticate by passing the token in the Authorization header:
        Authorization: Token <key>
    """

    def authenticate(self, request):
        auth = request.META.get('HTTP_AUTHORIZATION', '').split()

        if not auth or auth[0].lower() != 'token':
            return None

        if len(auth) == 1:
            raise AuthenticationFailed('Invalid token header. No credentials provided.')
        elif len(auth) > 2:
            raise AuthenticationFailed('Invalid token header. Token string should not contain spaces.')

        try:
            token = Token.objects.select_related('user').get(key=auth[1])
        except Token.DoesNotExist:
            raise AuthenticationFailed('Invalid token.')

        return (token.user, token)
