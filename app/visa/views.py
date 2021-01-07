import logging

import falcon

from app import queue
from app.prometheus import counter

log = logging.getLogger(__name__)


class VisaView:
    def on_post(self, req: falcon.Request, resp: falcon.Response):
        provider = "visa"

        # we always succeed the request, even if something fails later.
        resp.media = {"error_msg": "", "status_code": "0"}

        try:
            vop_tx_type = req.media["UserDefinedFieldsCollection"][0]["Value"].lower()
        except Exception as ex:
            log.warning(f"Couldn't find UserDefinedFieldsCollection.0.Value for Visa transaction: {repr(ex)}")
            return

        if vop_tx_type == "auth":
            tx_type = "auth"
        elif vop_tx_type == "settle":
            tx_type = "settlement"
        else:
            log.warning(f"Received an unsupported {vop_tx_type} Visa transaction: {req.media}")
            return

        counter.labels(payment_card=provider, type=tx_type).inc()
        queue.add(req.media, provider=provider, queue_name=f"{provider}-{tx_type}")
