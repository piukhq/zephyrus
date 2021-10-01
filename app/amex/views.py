import falcon

from app import queue
from app.amex import jwt_auth
from app.prometheus import counter
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
        counter.labels(payment_card="amex", type="auth").inc()
        queue.add(
            req.media,
            provider="amex",
            queue_name="amex-auth",
            span=req.context.scope.span,
        )
        resp.media = {"success": True}


class AmexSettlementView:
    @jwt_auth
    def on_post(self, req: falcon.Request, resp: falcon.Response):
        counter.labels(payment_card="amex", type="settle").inc()
        queue.add(
            req.media,
            provider="amex",
            queue_name="amex-settlement",
            span=req.context.scope.span,
        )
        resp.media = {"success": True}
