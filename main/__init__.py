import os
from importlib import import_module

import pusher
from flask import Flask, g
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from . import event_bus
from .commons.error_handlers import register_error_handlers
from .config import config
from .libs.diskcache_client import DiskcacheClient
from .libs.memcache_client import MemcacheClient


def _init_pusher():
    pusher_client = pusher.Pusher(
        app_id=config.PUSHER_APP_ID,
        key=config.PUSHER_KEY,
        secret=config.PUSHER_SECRET,
    )
    return pusher_client


def _init_memcache():
    return MemcacheClient(
        config.MEMCACHED_SERVERS,
        prefix_key=config.MEMCACHED_KEY_PREFIX,
        debug=1,
    )


app = Flask(__name__)
app.config.from_object(config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
pusher_client = _init_pusher()

CORS(app)

memcache_client = _init_memcache()
diskcache_client: DiskcacheClient = DiskcacheClient(
    directory=config.DISKCACHE_DIRECTORY,
    size_limit=config.DISKCACHE_SIZE_LIMIT,
    memcache_client=memcache_client,
)


def register_subpackages():
    from main import models

    for m in models.__all__:
        import_module('main.models.' + m)

    import main.controllers  # noqa


register_subpackages()
register_error_handlers(app)


@app.after_request
def execute_delayed_deferred(response):
    if os.getenv('ENVIRONMENT') == 'test':
        return response
    for task in getattr(g, 'delayed_tasks', []):
        event_bus.send_task(task)
    return response
