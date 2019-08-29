import falcon

from app.mastercard import mastercard_signed_xml_response
from app import queue


class MasterCardView:
    @mastercard_signed_xml_response
    def on_post(self, req: falcon.Request, resp: falcon.Response):
        queue.add(req.context.transaction_data, provider="mastercard")
        return {"success": True}
