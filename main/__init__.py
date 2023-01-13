from importlib import import_module

import pusher
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from .commons.error_handlers import register_error_handlers
from .config import config


def _init_pusher():
    pusher_client = pusher.Pusher(
        app_id=config.PUSHER_APP_ID,
        key=config.PUSHER_KEY,
        secret=config.PUSHER_SECRET,
    )
    return pusher_client


app = Flask(__name__)
app.config.from_object(config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
pusher_client = _init_pusher()

CORS(app)


def register_subpackages():
    from main import models

    for m in models.__all__:
        import_module('main.models.' + m)

    import main.controllers  # noqa


register_subpackages()
register_error_handlers(app)
