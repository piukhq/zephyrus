import falcon
import arrow
import jose.jwt

import settings


def get_params(req: falcon.Request, *params):
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
