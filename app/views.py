from decimal import Decimal

import voluptuous
from flask import request
from flask_restplus import Resource
from app.mastercard.process_xml_request import mastercard_signed_xml_response
from app import CustomException
from app.utils import save_transaction
from app.authentication.amex import jwt_auth
from app.errors import INVALID_DATA_FORMAT
from app import schema


class Amex(Resource):
    @jwt_auth
    def post(self):
        data = request.json
        conversion_map = {
            'transaction_time': 'time',
            'transaction_id': 'auth_code',
            'transaction_amount': 'amount',
            'cm_alias': 'payment_card_token',
            'merchant_number': 'mid',
            'offer_id': 'third_party_id',
        }

        transaction = {conversion_map[element[0]]: element[1]
                       for element in data.items() if element[0] in conversion_map}

        transaction['currency_code'] = 'GBP'

        try:
            schema.auth_transaction(transaction)
        except voluptuous.error.Invalid as e:
            raise CustomException(INVALID_DATA_FORMAT, e) from e

        transaction['amount'] = int(Decimal(transaction['amount']) * 100)  # conversion to pence

        save_transaction(transaction)

        return {'success': True}


class MasterCard(Resource):

    @mastercard_signed_xml_response
    def post(self):
        transaction = request.transaction_data
        try:
            schema.auth_transaction(transaction)
        except voluptuous.error.Invalid as e:
            raise CustomException(INVALID_DATA_FORMAT, e) from e

        transaction['amount'] = int(Decimal(transaction['amount']) * 100)  # conversion to pence
        save_transaction(transaction)
        return {'success': True}
