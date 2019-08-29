import falcon
from app import queue
from app.visa import base_auth


class VisaView:
    @base_auth
    def on_post(self, req: falcon.Request, resp: falcon.Response):
        queue.add(req.media, provider="visa")
        resp.media = {"error_msg": "", "status_code": "0"}
