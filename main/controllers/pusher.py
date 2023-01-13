# TODO: to be open sourced
from flask import jsonify, request

from main import app, auth
from main.commons import exceptions
from main.engines import pusher


@app.route('/pusher/auth', methods=['POST'])
@auth.require_account_token_auth()
def auth_pusher(account):
    response = pusher.authenticate(request, account)

    if not response:
        raise exceptions.Unauthorized()

    return jsonify(response)
