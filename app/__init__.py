import logging

from flask import Flask
from flask_redis import FlaskRedis
from raven.contrib.flask import Sentry

import settings
from app.errors import CustomException
from app.version import __version__

redis_store = FlaskRedis()
sentry = Sentry()


def create_app(config_name='settings'):
    from app.urls import api
    app = Flask(__name__)

    app.config.from_object(config_name)

    if settings.SENTRY_DSN:
        sentry.init_app(
            app,
            dsn=settings.SENTRY_DSN,
            logging=True,
            level=logging.ERROR)
        sentry.client.release = __version__

    api.init_app(app)
    redis_store.init_app(app)

    @api.errorhandler(CustomException)
    def handle_custom_exception(error):
        response = error.to_dict()
        return response, error.code

    return app
