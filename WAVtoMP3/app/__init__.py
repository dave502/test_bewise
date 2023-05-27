import os
import sys
from flask import Flask
from logging.handlers import RotatingFileHandler

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import StreamHandler
from app.logconfig import PackagePathFilter

app = Flask(__name__)
app.config.from_object("app.config.Config")
db = SQLAlchemy(app)
migrate = Migrate()


def create_app():

    migrate.init_app(app, db)

    from app.routes import app_route
    app.register_blueprint(app_route)

    app.logger.handlers.clear()

    app.debug = os.getenv("FLASK_DEBUG", False)

    if app.debug:
        log_handler = StreamHandler(stream=sys.stdout)
    else:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        log_handler = RotatingFileHandler('logs/app.log',
                                           maxBytes=10240, backupCount=10)

    log_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(relativepath)s:%(lineno)d]'))
    log_handler.addFilter(PackagePathFilter())
    log_handler.setLevel(logging.DEBUG if app.debug else logging.INFO)
    app.logger.addHandler(log_handler)
    app.logger.setLevel(logging.DEBUG if app.debug else logging.INFO)
    app.logger.info('App startup')

    return app

