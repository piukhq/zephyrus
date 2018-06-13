from flask import request, jsonify, make_response
from flask_restplus import Resource

from app.clients import ClientInfo
from app.errors import CLIENT_SECRET_DOES_NOT_MATCH, CustomException


class Auth(Resource):
    def post(self):
        client_id = request.json['client_id']
        client_secret = request.json['client_secret']

        client_info_store = ClientInfo()
        client = client_info_store.get_client(client_id)

        if client['secret'] != client_secret:
            raise CustomException(CLIENT_SECRET_DOES_NOT_MATCH)

        # if match, generate and return token/api key, else return error

        return make_response(jsonify(client))


class Amex(Resource):
    def post(self):
        return {'success': True}


class MasterCard(Resource):
    def post(self):
        return {'success': True}
