import urllib.parse
from functools import wraps

import jwt
from flask import request

from main import jwttoken
from main.commons import exceptions
from main.enums import AccountStatus, AudienceType
from main.models.account import AccountModel


def parse_access_token():
    # Parse authorization header.
    # For access token authorization, the header will have the formation: Bearer <access_token>
    authorization = None
    cookie_key = 'gotit.query-ai.m340.configuration-portal.authentication'

    if 'Authorization' in request.headers:
        authorization = request.headers['Authorization']
    elif cookie_key in request.cookies:
        authorization = urllib.parse.unquote(request.cookies[cookie_key])

    if not authorization:
        raise exceptions.EmptyAuthorizationHeader()

    if not authorization.startswith('Bearer '):
        raise exceptions.InvalidAuthorizationHeader()
    # Parse access token from the authorization header
    return authorization[len('Bearer ') :]


def get_account(access_token, require_fresh_access_token=False):
    try:
        token = jwttoken.decode(access_token, AudienceType.ACCOUNT)
    except jwt.ExpiredSignatureError:
        raise exceptions.ExpiredAccessToken()
    except jwt.InvalidTokenError:
        raise exceptions.InvalidAccessToken()
    if 'fresh' not in token:
        raise exceptions.InvalidAccessToken()
    if require_fresh_access_token and token['fresh'] is False:
        raise exceptions.FreshAccessTokenRequired()
    # Get account from decoded token
    account = AccountModel.query.get(token['sub'])

    if account.status != AccountStatus.ACTIVE:
        raise exceptions.InactiveAccount(error_data={'email': account.email})

    return account


def require_account_token_auth():
    def require_token_auth_decorator(f):
        @wraps(f)
        def wrapper(**kwargs):
            kwargs[AudienceType.ACCOUNT] = get_account(
                access_token=parse_access_token()
            )
            return f(**kwargs)

        return wrapper

    return require_token_auth_decorator
