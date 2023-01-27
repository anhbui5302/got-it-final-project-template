from flask import jsonify

from main import app, auth, config
from main.commons import exceptions
from main.core import parse_args_with
from main.engines.exceptions import TokenException
from main.engines.token import create_tokens, generate_tokens, get_token, revoke_tokens
from main.enums import AccountStatus
from main.libs.google_auth import GoogleAuthException, get_google_user_info
from main.models.account import AccountModel
from main.schemas.authentication import (
    OAuthGoogleSchema,
    TokensRefreshingSchema,
    TokensRevokingSchema,
)


def validate_email_domain(email: str):
    email = email.strip().lower()
    if '@' not in email:
        raise exceptions.BadRequest(error_message='Invalid email format.')
    email_domain = email.split('@')[1]
    if email_domain not in config.ALLOWED_DOMAINS:
        raise exceptions.BadRequest(error_message='Invaid email domain.')


def get_account(
    email: str,
) -> AccountModel:
    """
    Get an account from email
    :param email: Member email
    :return:
    """
    # Find an account that's associated with the email
    # account = AccountModel.query.filter_by(email=email).one_or_none()
    # Temporarily, all super admins share the same account '*@bot-it.ai'
    account = AccountModel.query.filter(AccountModel.email == '*@bot-it.ai').first()
    if account is None:
        raise exceptions.AccountNotFound(
            error_message='You are not able to login to this portal.',
            error_data={'email': email},
        )
    # Check the status of the account
    if account.status != AccountStatus.ACTIVE:
        raise exceptions.InactiveAccount(
            error_message='You are not able to login to this portal.',
            error_data={'email': email},
        )

    return account


@app.route('/access-tokens/google', methods=['POST'])
@parse_args_with(OAuthGoogleSchema())
def admin_sign_in_with_google(args: dict):
    try:
        google_user = get_google_user_info(args['id_token'], config.GOOGLE_CLIENT_ID)
    except GoogleAuthException:
        raise exceptions.BadRequest(
            error_message='Could not fetch your Google account information. Please try again later.'
        )

    email = google_user['email']
    validate_email_domain(email)

    account = get_account(email)
    tokens = create_tokens(account)
    return jsonify(tokens)


@app.route('/access-tokens/refresh', methods=['POST'])
@parse_args_with(TokensRefreshingSchema())
def admin_refresh_tokens(args: dict, **__):
    token = get_token(args['refresh_token'])
    if token is None or token.is_expired:
        raise exceptions.Unauthorized(
            error_message='Token does not exist or is expired.'
        )

    tokens = generate_tokens(token)
    return jsonify(tokens)


@app.route('/access-tokens/revoke', methods=['POST'])
@auth.require_account_token_auth()
@parse_args_with(TokensRevokingSchema())
def admin_revoke_tokens(args: dict, account: AccountModel, **__):
    try:
        revoke_tokens(args['refresh_token'], account.id)
    except TokenException as e:
        raise exceptions.Unauthorized(error_message=e.message)
    return jsonify({})
