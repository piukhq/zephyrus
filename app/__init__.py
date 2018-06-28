from flask import Flask
from flask_redis import FlaskRedis

from app.errors import CustomException

redis_store = FlaskRedis()


def create_app(config_name='settings'):
    from app.urls import api
    app = Flask(__name__)

    app.config.from_object(config_name)
    api.init_app(app)
    redis_store.init_app(app)

    @api.errorhandler(CustomException)
    def handle_custom_exception(error):
        response = error.to_dict()
        return response, error.code

    return app
