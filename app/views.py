import voluptuous
from flask import request
from flask_restplus import Resource

from app import CustomException
from app.amex.utils import save_transaction, format_data
from app.authentication.amex import jwt_auth
from app.errors import INVALID_DATA_FORMAT
from app import schema


class Amex(Resource):
    @jwt_auth
    def post(self):
        data = request.json
        try:
            schema.amex_auth_transaction(data)
        except voluptuous.error.Invalid as e:
            raise CustomException(INVALID_DATA_FORMAT, e) from e

        transaction = format_data(data)
        save_transaction(transaction)

        return {'success': True}


class MasterCard(Resource):

    @mastercard_signed_xml
    def post(self):
        data = request.data
        print(data)
        # todo: Commment out when merged with Development
        #try:
        #    schema.mastercard_auth_transaction(data)
        #except voluptuous.error.Invalid as e:
        #    raise CustomException(INVALID_DATA_FORMAT, e) from e
        #transaction = format_data(data)
        #save_transaction(transaction)
        return {'success': True}
