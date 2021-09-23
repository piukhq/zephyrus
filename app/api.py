import falcon
import sentry_sdk
from falcon.media import Handlers, JSONHandler
from sentry_sdk.integrations.falcon import FalconIntegration

from app.amex import AmexAuthView, AmexSettlementView, AmexView
from app.errors import CustomException
from app.mastercard import MasterCardView
from app.prometheus import PrometheusHandler
from app.views import HealthCheck, LivezCheck, ReadyzCheck
from app.visa import VisaView


class RawXMLHandler(JSONHandler):
    def deserialize(self, stream, content_type, content_length):
        return stream.read()

    def serialize(self, media, content_type):
        return media


def handle_custom_exception(error: CustomException, req: falcon.Request, resp: falcon.Response, *params) -> None:
    resp.media = error.to_dict()
    resp.status = error.code


def create_app() -> falcon.API:
    app = falcon.API()

    sentry_sdk.init(integrations=[FalconIntegration()])

    app.add_error_handler(CustomException, handle_custom_exception)
    app.req_options.media_handlers = Handlers(
        {
            "application/json": JSONHandler(),
            "application/json; charset=UTF-8": JSONHandler(),
            "application/xml": RawXMLHandler(),
            "text/xml": RawXMLHandler(),
        }
    )

    app.add_route("/auth_transactions/visa", VisaView())
    app.add_route("/auth_transactions/mastercard", MasterCardView)
    app.add_route("/healthz", HealthCheck())
    app.add_route("/livez", LivezCheck())
    app.add_route("/readyz", ReadyzCheck())
    app.add_route("/auth_transactions/authorize", AmexAuthView)
    app.add_route("/auth_transactions/amex", AmexView)
    app.add_route("/auth_transactions/amex/settlement", AmexSettlementView)
    app.add_route("/metrics", PrometheusHandler)
    return app
