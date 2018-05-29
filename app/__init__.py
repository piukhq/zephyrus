from flask import Flask


def create_app(config_name='settings'):
    app = Flask(__name__)

    app.config.from_object(config_name)

    return app
