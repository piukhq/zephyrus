from typing import TYPE_CHECKING

import jose.exceptions
import jose.jwt
from app.security import load_secrets
from app.errors import (
    AuthException,
    MISSING_AUTH,
    INVALID_AUTH_FORMAT,
    INVALID_AUTH_TYPE,
    AUTH_EXPIRED,
    INVALID_AUTH_TOKEN
)

if TYPE_CHECKING:
    import falcon


def jwt_auth(f):
    def check_auth(req: "falcon.Request", resp: "falcon.Response", *args, **kwargs):
        auth_header = req.auth
        if not auth_header:
            raise AuthException(MISSING_AUTH)

        try:
            auth_type, token = auth_header.split(" ", 1)
        except ValueError:
            raise AuthException(INVALID_AUTH_FORMAT)

        if auth_type.lower() != "token":
            raise AuthException(INVALID_AUTH_TYPE, auth_type.title())

        try:
            client_secrets = load_secrets()
            jose.jwt.decode(
                token, key=client_secrets['amex']['secret'], audience="https://api.bink.com", issuer="bink"
            )
        except jose.exceptions.ExpiredSignatureError as e:
            raise AuthException(AUTH_EXPIRED) from e
        except jose.exceptions.JWTError as e:
            raise AuthException(INVALID_AUTH_TOKEN) from e

        return f(f, req, resp, *args, **kwargs)

    return check_auth
