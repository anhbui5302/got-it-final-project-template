from flask import jsonify

from main import app, auth
from main.core import parse_args_with
from main.engines.pusher import trigger_rasa_status_changed
from main.schemas.project import RasaStatusChangedSchema


@app.route('/webhook/notify-rasa-status-changed', methods=['POST'])
@auth.require_application_auth()
@parse_args_with(RasaStatusChangedSchema())
def notify_rasa_status_changed(args, **__):
    trigger_rasa_status_changed(args)
    return jsonify({})
