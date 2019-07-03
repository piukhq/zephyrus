import base64
from functools import wraps

import arrow
import jose.jwt

import settings
from app.clients import ClientInfo
from app.errors import INVALID_CLIENT_SECRET, AuthException, MISSING_PARAMS, CustomException, MISSING_AUTH, \
    INVALID_AUTH_FORMAT, INVALID_AUTH_TYPE, INVALID_AUTH_TOKEN, AUTH_EXPIRED, CLIENT_DOES_NOT_EXIST, \
    INVALID_AUTH_SETTINGS


def get_params(*params):
    values = []
    missing = []
    for param in params:
        try:
            value = request.json[param]
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


def jwt_auth(f):
    @wraps(f)
    def check_auth(request, response, *args, **kwargs):
        try:
            auth_header = request.headers['Authorization']
        except KeyError:
            raise AuthException(MISSING_AUTH)

        try:
            auth_type, token = auth_header.split(' ', 1)
        except ValueError:
            raise AuthException(INVALID_AUTH_FORMAT)

        if auth_type.lower() != 'token':
            raise AuthException(INVALID_AUTH_TYPE, auth_type.title())

        try:
            claims = jose.jwt.decode(
                token,
                key=settings.SIGNATURE_SECRET,
                audience='https://api.bink.com',
                issuer='bink')
        except jose.exceptions.ExpiredSignatureError as e:
            raise AuthException(AUTH_EXPIRED) from e
        except jose.exceptions.JWTError as e:
            raise AuthException(INVALID_AUTH_TOKEN) from e

        try:
            g.client = ClientInfo.get_client(claims['sub'])
        except CustomException:
            raise AuthException(CLIENT_DOES_NOT_EXIST)

        return f(*args, **kwargs)

    return check_auth


class Auth:
    def on_post(self, request, response):
        params, missing = get_params('client_id', 'client_secret')

        if missing:
            raise AuthException(MISSING_PARAMS, missing)

        client_id, client_secret = params
        client_info_store = ClientInfo()

        # If redis was just updated by hermes (ClientInfo().data is not None), check against the data from
        # hermes' response instead of accessing redis again.
        client = {}
        if client_info_store.data:
            for client_object in client_info_store.data:
                if client_id == client_object['client_id']:
                    client = client_object
                    break

            if not client:
                raise AuthException(CLIENT_DOES_NOT_EXIST)
        else:
            client = client_info_store.get_client(client_id)

        if client['secret'] != client_secret:
            raise AuthException(INVALID_CLIENT_SECRET)

        # if match, generate and return token/api key, else return error
        response.media = {
            'api_key': generate_jwt(client)
        }


class Me:
    @jwt_auth
    def get(self, request, response):
        response.media = {'identity': g.client['organisation']}


def _check_visa_auth(token: str) -> bool:
    if not (settings.VISA_CREDENTIALS['username'] and settings.VISA_CREDENTIALS['password']):
        raise AuthException(INVALID_AUTH_SETTINGS)

    username, password = base64.b64decode(token).decode('utf-8').split(':')
    return username == settings.VISA_CREDENTIALS['username'] and password == settings.VISA_CREDENTIALS['password']


def visa_auth(f):
    def decorated(request, response):
        try:
            auth_type, token = request.auth.split(' ')
        except (AttributeError, ValueError):
            raise AuthException(INVALID_AUTH_TOKEN)

        if auth_type.lower() != 'basic' or not _check_visa_auth(token):
            raise AuthException(INVALID_AUTH_TOKEN)

        return f(f, request, response)

    return decorated
