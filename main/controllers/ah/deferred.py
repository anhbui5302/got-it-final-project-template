# TODO: to be open sourced
import base64
import pickle

from flask import jsonify, request

from main import app
from main.libs.log import ServiceLogger

logger = ServiceLogger(__name__)


@app.route('/_ah/eb_queue/deferred_flask', methods=['POST'])
@app.route('/_ah/eb_queue/deferred_flask/<deferred_func>', methods=['POST'])
def run_deferred_eventbus(deferred_func='Unknown'):
    try:
        func, args, kwargs = pickle.loads(base64.decodestring(request.data))
        func(*args, **kwargs)
    except Exception as e:
        logger.exception(message=str(e))

    return jsonify({})
