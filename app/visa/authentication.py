import base64
import binascii

import falcon
import settings
from app.errors import AuthException, INVALID_AUTH_SETTINGS, INVALID_AUTH_TOKEN


def _check_visa_auth(token: str) -> bool:
    if not (settings.VISA_CREDENTIALS["username"] and settings.VISA_CREDENTIALS["password"]):
        raise AuthException(INVALID_AUTH_SETTINGS)
    try:
        username, password = base64.b64decode(token).decode("utf-8").split(":")
    except (binascii.Error, ValueError):
        return False

    return username == settings.VISA_CREDENTIALS["username"] and password == settings.VISA_CREDENTIALS["password"]


def base_auth(f):
    def decorated(req: falcon.Request, resp: falcon.Response):
        try:
            auth_type, token = req.auth.split(" ")
        except (AttributeError, ValueError):
            raise AuthException(INVALID_AUTH_TOKEN)

        if auth_type.lower() != "basic" or not _check_visa_auth(token):
            raise AuthException(INVALID_AUTH_TOKEN)

        return f(f, req, resp)

    return decorated
