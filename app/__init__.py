from flask import Flask


def create_app(config_filename=None):
    config_filename = config_filename or '../instance/config.py'

    app = Flask(__name__)
    app.config.from_pyfile(config_filename)
    app.secret_key = app.config['SECRET_KEY']

    return app


create_app()
