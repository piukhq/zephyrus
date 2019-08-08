import falcon
import sentry_sdk
from falcon.media import JSONHandler, Handlers
from sentry_sdk.integrations.falcon import FalconIntegration

import settings
from app import urls
from app.errors import CustomException


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
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            integrations=[FalconIntegration()],
        )

    app.add_error_handler(CustomException, handle_custom_exception)
    app.req_options.media_handlers = Handlers({
        'application/json': JSONHandler(),
        'application/json; charset=UTF-8': JSONHandler(),
        'application/xml': RawXMLHandler(),
        'text/xml': RawXMLHandler()
    })

    for url in urls.urlpatterns:
        app.add_route(**url._asdict())

    return app
