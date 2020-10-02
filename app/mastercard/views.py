import falcon

from app.mastercard import mastercard_signed_xml_response
from app import queue
from app.prometheus import counters


class MasterCardView:
    @mastercard_signed_xml_response
    def on_post(self, req: falcon.Request, resp: falcon.Response):
        counters["mastercard"].inc()
        queue.add(req.context.transaction_data, provider="mastercard", queue_name="mastercard-auth")
