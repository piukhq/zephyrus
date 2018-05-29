from flask import Flask


def create_app(config_name='settings'):
    from app.views import api
    app = Flask(__name__)

    app.config.from_object(config_name)
    api.init_app(app)

    return app
