from flask import request, jsonify, make_response
from flask_restplus import Resource

from app.clients import ClientInfo
from app.errors import INVALID_CLIENT_SECRET, AuthException, MISSING_PARAMS


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

        return make_response(jsonify(client))


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
