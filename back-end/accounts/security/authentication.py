import jwt
from django.utils import timezone
from drf_spectacular.extensions import OpenApiAuthenticationExtension
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed

from accounts.security import tokens
from accounts.models import AuthSession
from accounts.services.shared.account_rules import is_account_usable
from accounts.services.shared.sessions import SESSION_ENDED


class SessionTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        header = get_authorization_header(request).split()
        if not header or header[0].lower() != b"bearer":
            return None
        if len(header) != 2:
            raise AuthenticationFailed("Send the access token as 'Authorization: Bearer <token>'.")
        try:
            claims = tokens.decode_access_token(header[1].decode())
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Your access token has expired. Refresh it and try again.")
        except (jwt.PyJWTError, UnicodeDecodeError):
            raise AuthenticationFailed("Your access token is invalid. Sign in again.")

        now = timezone.now()
        session = (
            AuthSession.objects.for_access_token(claims["sid"], claims["sub"]).first()
        )
        if (
            session is None
            or session.revoked_at is not None
            or session.expires_at <= now
            or not is_account_usable(session.user, now)
        ):
            raise AuthenticationFailed(SESSION_ENDED)
        return session.user, session

    def authenticate_header(self, request):
        return 'Bearer realm="api"'


class SessionTokenScheme(OpenApiAuthenticationExtension):
    target_class = SessionTokenAuthentication
    name = "bearerAuth"

    def get_security_definition(self, auto_schema):
        return {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
