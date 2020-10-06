import falcon
from app import queue
from app.prometheus import counter


class VisaView:
    def on_post(self, req: falcon.Request, resp: falcon.Response):
        provider = "visa"
        user_fields_collection = req.media.get("UserDefinedFieldsCollection")
        if user_fields_collection and user_fields_collection[0].get("Value").lower() == "auth":
            tx_type = "auth"
        else:
            tx_type = "settlement"
        counter.labels(payment_card=provider, type=tx_type).inc()
        queue.add(req.media, provider=provider, queue_name=f"{provider}-{tx_type}")
        resp.media = {"error_msg": "", "status_code": "0"}
