from functools import wraps

import arrow
import jose.jwt
from flask import request, jsonify, make_response, g
from flask_restplus import Resource

import settings
from app.clients import ClientInfo
from app.errors import INVALID_CLIENT_SECRET, AuthException, MISSING_PARAMS, CustomException, MISSING_AUTH, \
    INVALID_AUTH_FORMAT, INVALID_AUTH_TYPE, INVALID_AUTH_TOKEN, AUTH_EXPIRED, CLIENT_DOES_NOT_EXIST


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
    def check_auth(*args, **kwargs):
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


class Auth(Resource):
    def post(self):
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
        response = jsonify({
            'api_key': generate_jwt(client)
        })

        return make_response(response)


class Me(Resource):
    @jwt_auth
    def get(self):
        return make_response(jsonify({'identity': g.client['organisation']}))


def _check_visa_auth(username: str, password: str) -> bool:
    return username == settings.VISA_CREDENTIALS['username'] and password == settings.VISA_CREDENTIALS['password']


def visa_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not _check_visa_auth(auth.username, auth.password):
            raise AuthException(INVALID_AUTH_TOKEN)
        return f(*args, **kwargs)

    return decorated
