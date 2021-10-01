import falcon

from app import queue
from app.mastercard import mastercard_signed_xml_response
from app.prometheus import counter


class MasterCardView:
    @mastercard_signed_xml_response
    def on_post(self, req: falcon.Request, resp: falcon.Response):
        counter.labels(payment_card="mastercard", type="auth").inc()
        queue.add(
            req.context.transaction_data,
            provider="mastercard",
            queue_name="mastercard-auth",
            span=req.context.scope.span,
        )
