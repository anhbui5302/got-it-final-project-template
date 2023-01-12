# TODO: to be open sourced
import datetime

import jwt

from main.config import config
from main.models.account import AccountModel


def encode(
    account: AccountModel, lifetime=config.ACCESS_TOKEN_LIFETIME, is_fresh: bool = False
):
    iat = datetime.datetime.utcnow()
    return jwt.encode(
        {
            'sub': account.id,
            'aud': account.audience_type,
            'iat': iat,
            'exp': iat + datetime.timedelta(seconds=lifetime),
            'fresh': is_fresh,
        },
        config.JWT_SECRET,
    )


def decode(access_token, audience):
    token = jwt.decode(
        access_token,
        config.JWT_SECRET,
        leeway=10,
        algorithms='HS256',
        audience=audience,
    )
    return token
