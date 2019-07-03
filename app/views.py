from decimal import Decimal

import sentry_sdk
import voluptuous

from app import schema
from app.authentication.token_utils import jwt_auth, visa_auth
from app.errors import CustomException, INVALID_DATA_FORMAT
from app.mastercard.process_xml_request import mastercard_signed_xml_response
from app.utils import save_transaction, format_visa_transaction


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import falcon


class HealthCheck:
    def on_get(self, req: 'falcon.Request', resp: 'falcon.Response'):
        resp.media = ''


class Amex:
    @jwt_auth
    def on_post(self, req: 'falcon.Request', resp: 'falcon.Response'):
        data = req.media
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
        resp.media = {'success': True}


class MasterCard:

    @mastercard_signed_xml_response
    def on_post(self, req: 'falcon.Request', resp: 'falcon.Response'):
        transaction = req.context.transaction_data
        try:
            schema.auth_transaction(transaction)
        except voluptuous.error.Invalid as e:
            sentry_sdk.capture_exception(e)
            raise CustomException(INVALID_DATA_FORMAT, e) from e
        else:
            transaction['amount'] = int(Decimal(transaction['amount']) * 100)  # conversion to pence
            save_transaction(transaction)
            resp.media = {'success': True}


class Visa:

    @visa_auth
    def on_post(self, req: 'falcon.Request', resp: 'falcon.Response'):
        try:
            data = schema.visa_auth_transaction(req.media)
            formatted_transaction = format_visa_transaction(data)
        except (voluptuous.error.Invalid, KeyError) as e:
            sentry_sdk.capture_exception(e)
            resp.media = {'status_code': 100, 'error_msg': e.error_message}
        else:
            save_transaction(formatted_transaction)
            resp.media = {'error_msg': '', 'status_code': '0'}
