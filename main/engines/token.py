from datetime import datetime
from typing import Optional

from main import db, jwttoken
from main.engines.exceptions import TokenException
from main.enums import TokenType
from main.models.account import AccountModel
from main.models.token import TokenModel


def get_token(value: str) -> Optional[TokenModel]:
    return TokenModel.query.filter_by(value=value).one_or_none()


def create_token(
    account_id: int,
    type_: str,
    value: str = None,
    expiration_time: Optional[datetime] = None,
) -> TokenModel:
    token = TokenModel(
        account_id=account_id,
        type=type_,
        value=value,
        expiration_time=expiration_time,
    )
    db.session.add(token)
    return token


def delete_token(value: str):
    TokenModel.query.filter_by(value=value).delete()


def cleanup_expired_tokens():
    """This function is executed periodically by a cron job."""

    TokenModel.query.filter(TokenModel.expiration_time <= datetime.utcnow()).delete()
    db.session.commit()


def create_tokens(account: AccountModel) -> dict:
    """Use this function when signing in or signing up."""
    refresh_token = create_token(
        account_id=account.id,
        type_=TokenType.REFRESH_TOKEN,
    )
    access_token = create_access_token(account, is_fresh=True)
    db.session.commit()

    return {
        'access_token': access_token,
        'refresh_token': refresh_token.value,
    }


def generate_tokens(token: TokenModel):
    # Create a new refresh token and delete old one
    new_refresh_token = create_token(
        account_id=token.account_id,
        type_=TokenType.REFRESH_TOKEN,
    )
    delete_token(token.value)
    db.session.commit()

    # Generate a new non-fresh access token
    new_access_token = create_access_token(new_refresh_token.account, is_fresh=False)
    return {
        'access_token': new_access_token,
        'refresh_token': new_refresh_token.value,
    }


def revoke_tokens(refresh_token: str, account_id: int):
    token = get_token(refresh_token)
    if not token or token.account_id != account_id:
        raise TokenException(message='Invalid token.')

    delete_token(refresh_token)
    db.session.commit()


def create_access_token(account: AccountModel, is_fresh: bool = True):
    """
    Generate access token for a member
    :param account: super admin
    :param is_fresh: indicate if the access token is fresh or not
    :return: access token
    """
    return jwttoken.encode(account, is_fresh=is_fresh)
