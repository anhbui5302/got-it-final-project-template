import urllib.parse
from functools import wraps

import jwt
from flask import request

from main import application_jwttoken, jwttoken
from main.commons import exceptions
from main.enums import AccountStatus, ApplicationStatus, AudienceType
from main.models.account import AccountModel
from main.models.application import ApplicationModel


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


def get_application(access_token):
    # Decode the access token which has been passed in the request headers without validation
    token = application_jwttoken.decode(access_token, verify=False)
    if not token:
        raise exceptions.InvalidAccessToken()
    application_key = token.get('iss')
    if not application_key:
        raise exceptions.InvalidAccessToken()
    application = ApplicationModel.query.filter_by(
        application_key=application_key
    ).first()
    if not application:
        raise exceptions.InvalidAccessToken()
    # Decode the token using the application secret
    token = application_jwttoken.decode(
        access_token, secret=application.application_secret, verify=True
    )
    if not token:
        raise exceptions.InvalidAccessToken()
    if application.status != ApplicationStatus.ACTIVE:
        raise exceptions.Unauthorized(
            error_code=exceptions.ApplicationErrorCode.INACTIVE_APPLICATION,
            error_message=exceptions.ApplicationErrorMessage.INACTIVE_APPLICATION,
        )
    return application


def require_application_auth():
    def require_application_auth_decorator(f):
        @wraps(f)
        def wrapper(**kwargs):
            kwargs[AudienceType.APPLICATION] = get_application(
                access_token=parse_access_token()
            )
            return f(**kwargs)

        return wrapper

    return require_application_auth_decorator
