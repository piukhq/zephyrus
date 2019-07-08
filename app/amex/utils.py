from typing import TYPE_CHECKING

import arrow
import jose.jwt

import settings

if TYPE_CHECKING:
    import falcon


def get_params(req: 'falcon.Request', *params):
    values = []
    missing = []
    for param in params:
        try:
            value = req.media[param]
        except (KeyError, TypeError):
            missing.append(param)
        else:
            values.append(value)
    return values, missing


def generate_jwt(client):
    time_now = arrow.now()
    claims = {
        'exp': time_now.replace(minutes=5).timestamp,
        'nbf': time_now.timestamp,
        'iss': 'bink',
        'aud': 'https://api.bink.com',
        'iat': time_now.timestamp,
        'sub': client['client_id']
    }
    return jose.jwt.encode(claims, key=settings.SIGNATURE_SECRET)
