import falcon
from app import queue


class VisaView:
    def on_post(self, req: falcon.Request, resp: falcon.Response):
        user_fields_collection = req.media.get("UserDefinedFieldsCollection")
        if user_fields_collection and user_fields_collection[0].get("Value").lower() == "auth":
            provider = "visa-auth"
        else:
            provider = "visa-settlement"
        queue.add(req.media, provider="visa", queue_name=provider)
        resp.media = {"error_msg": "", "status_code": "0"}
