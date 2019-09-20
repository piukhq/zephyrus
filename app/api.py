import falcon
import sentry_sdk
from falcon.media import JSONHandler, Handlers
from sentry_sdk.integrations.falcon import FalconIntegration

import settings
from app.errors import CustomException
from app.amex import AmexAuthView, AmexMeView, AmexView
from app.mastercard import MasterCardView
from app.views import HealthCheck
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

    if settings.SENTRY_DSN:
        sentry_sdk.init(dsn=settings.SENTRY_DSN, integrations=[FalconIntegration()])

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
    app.add_route("/auth_transactions/authorize", AmexAuthView)
    app.add_route("/me", AmexMeView)
    app.add_route("/auth_transactions/amex", AmexView)
    app.add_route("/auth_transactions/mastercard", MasterCardView)

    return app
