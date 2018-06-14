from functools import wraps

import jose.jwt
import maya
from flask import request, jsonify, make_response, g
from flask_restplus import Resource

import settings
from app.clients import ClientInfo
from app.errors import INVALID_CLIENT_SECRET, AuthException, MISSING_PARAMS, CustomException, MISSING_AUTH, \
    INVALID_AUTH_FORMAT, INVALID_AUTH_TYPE, INVALID_AUTH_TOKEN, AUTH_EXPIRED, CLIENT_DOES_NOT_EXIST


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
        else:
            client = client_info_store.get_client(client_id)

        if client['secret'] != client_secret:
            raise AuthException(INVALID_CLIENT_SECRET)

        # if match, generate and return token/api key, else return error
        response = jsonify({
            'api_key': generate_jwt(client)
        })

        return make_response(response)


def get_params(*params):
    values = []
    missing = []
    for param in params:
        try:
            value = request.json[param]
        except KeyError:
            missing.append(param)
        else:
            values.append(value)
    return values, missing


def generate_jwt(client):
    time_now = maya.now()
    claims = {
        'exp': time_now.add(minutes=5).epoch,
        'nbf': time_now.epoch,
        'iss': 'bink',
        'aud': 'https://api.bink.com',
        'iat': time_now.epoch,
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
        except jose.exceptions.ExpiredSignatureError:
            raise AuthException(AUTH_EXPIRED)
        except jose.exceptions.JWTError as e:
            print(repr(e))
            raise AuthException(INVALID_AUTH_TOKEN)

        try:
            g.client = ClientInfo.get_client(claims['sub'])
        except CustomException:
            raise AuthException(CLIENT_DOES_NOT_EXIST)

        return f(*args, **kwargs)
    return check_auth

