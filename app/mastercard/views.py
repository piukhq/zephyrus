from _pydecimal import Decimal
from typing import TYPE_CHECKING

import sentry_sdk
import voluptuous

import settings
from app.errors import CustomException, INVALID_DATA_FORMAT
from app.mastercard import mastercard_signed_xml_response
from app.schema import auth_transaction_schema
from app.utils import send_to_zagreus

if TYPE_CHECKING:
    import falcon


class MasterCardView:

    @mastercard_signed_xml_response
    def on_post(self, req: 'falcon.Request', resp: 'falcon.Response'):
        transaction = req.context.transaction_data
        try:
            auth_transaction_schema(transaction)
        except voluptuous.error.Invalid as e:
            if settings.SENTRY_DSN:
                sentry_sdk.capture_exception(e)
            raise CustomException(INVALID_DATA_FORMAT, e) from e
        else:
            transaction['amount'] = int(Decimal(transaction['amount']) * 100)  # conversion to pence
            send_to_zagreus(transaction, 'MASTERCARD')
            return {'success': True}
