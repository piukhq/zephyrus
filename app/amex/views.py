import falcon

from app import queue
from app.amex import jwt_auth
from app.security import generate_jwt


class AmexAuthView:
    @staticmethod
    def on_post(req: falcon.Request, resp: falcon.Response):
        jwt = generate_jwt('amex')
        if jwt:
            resp.media = {"api_key": jwt}
        else:
            resp.media = {}
            resp.status = falcon.HTTP_BAD_REQUEST


class AmexView:
    @jwt_auth
    def on_post(self, req: falcon.Request, resp: falcon.Response):
        queue.add(req.media, provider="amex")
        resp.media = {"success": True}
