import falcon

from app import queue
from app.amex import jwt_auth
from app.prometheus import counters
from app.security import generate_jwt


class AmexAuthView:
    @staticmethod
    def on_post(req: falcon.Request, resp: falcon.Response):
        jwt = generate_jwt("amex", req.media)
        if jwt:
            resp.media = {"api_key": jwt}
        else:
            resp.media = {}
            resp.status = falcon.HTTP_FORBIDDEN


class AmexView:
    @jwt_auth
    def on_post(self, req: falcon.Request, resp: falcon.Response):
        counters["amex"].inc()
        queue.add(req.media, provider="amex", queue_name="amex-auth")
        resp.media = {"success": True}
