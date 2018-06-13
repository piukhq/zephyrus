from flask import request, jsonify, make_response
from flask_restplus import Resource

from app.clients import ClientInfo
from app.errors import error_response, CLIENT_DOES_NOT_EXIST, CLIENT_SECRET_DOES_NOT_MATCH


class Auth(Resource):
    def post(self):
        client_id = request.json['client_id']
        client_secret = request.json['client_secret']

        try:
            client_info_store = ClientInfo()
            client = client_info_store.get_client(client_id)

            if client['secret'] == client_secret:
                result = jsonify(client)
            else:
                result = error_response(CLIENT_SECRET_DOES_NOT_MATCH)
        except AttributeError as e:
            result = error_response(CLIENT_DOES_NOT_EXIST)

        # If data, check if secret matches

        # if match, generate and return token/api key, else return error

        return make_response(result)


class Amex(Resource):
    def post(self):
        return {'success': True}


class MasterCard(Resource):
    def post(self):
        return {'success': True}
