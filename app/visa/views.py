from typing import TYPE_CHECKING

import sentry_sdk
import voluptuous

import settings
from app.utils import send_to_hermes, send_to_zagreus
from app.visa import base_auth, visa_transaction_schema, format_visa_transaction

if TYPE_CHECKING:
    import falcon


class VisaView:

    @base_auth
    def on_post(self, req: 'falcon.Request', resp: 'falcon.Response'):
        try:
            data = visa_transaction_schema(req.media)
            formatted_transaction = format_visa_transaction(data)
        except (voluptuous.error.Invalid, KeyError) as e:
            if settings.SENTRY_DSN:
                sentry_sdk.capture_exception(e)
            resp.media = {'status_code': 100, 'error_msg': e.error_message}
        else:
            send_to_zagreus(formatted_transaction, 'VISA')
            send_to_hermes(formatted_transaction)
            resp.media = {'error_msg': '', 'status_code': '0'}
