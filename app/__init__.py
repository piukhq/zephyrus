import falcon
import sentry_sdk
from sentry_sdk.integrations.falcon import FalconIntegration

import settings
from app import urls
from app.errors import CustomException
from app.version import __version__


def handle_custom_exception(error: CustomException, req: falcon.Request, resp: falcon.Response, *params) -> None:
    resp.media = error.to_dict()
    resp.status = error.code


def create_api() -> falcon.API:
    api = falcon.API()

    if settings.SENTRY_DSN:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            integrations=[FalconIntegration()],
        )

    api.add_error_handler(CustomException, handle_custom_exception)

    for url in urls.urlpatterns:
        api.add_route(**url._asdict())

    return api
