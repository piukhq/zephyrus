from _pydecimal import Decimal
from typing import TYPE_CHECKING

import voluptuous

from app.amex import get_params, generate_jwt, jwt_auth
from app.clients import ClientInfo
from app.errors import AuthException, MISSING_PARAMS, CLIENT_DOES_NOT_EXIST, INVALID_CLIENT_SECRET, CustomException, \
    INVALID_DATA_FORMAT
from app.schema import auth_transaction_schema
from app.utils import save_transaction

if TYPE_CHECKING:
    import falcon


class AmexAuthView:
    @staticmethod
    def on_post(req: 'falcon.Request', resp: 'falcon.Response'):
        params, missing = get_params(req, 'client_id', 'client_secret')

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
        resp.media = {
            'api_key': generate_jwt(client)
        }


class AmexMeView:
    @jwt_auth
    def on_get(self, req: 'falcon.Request', resp: 'falcon.Response'):
        resp.media = {'identity': req.context.client['organisation']}


class AmexView:
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
            auth_transaction_schema(transaction)
        except voluptuous.error.Invalid as e:
            raise CustomException(INVALID_DATA_FORMAT, e) from e

        transaction['amount'] = int(Decimal(transaction['amount']) * 100)  # conversion to pence
        save_transaction(transaction)
        resp.media = {'success': True}
