import datetime
import os

import jwt


def encode(application_key, application_secret):
    iat = datetime.datetime.utcnow()
    return jwt.encode(
        {
            'iss': application_key,
            'iat': iat,
            'jti': generate_nonce(),
        },
        application_secret,
    )


def decode(access_token, secret='', verify=True):
    try:
        token = jwt.decode(
            access_token,
            secret,
            options={'verify_signature': verify},
            algorithms='HS256',
        )
    except jwt.InvalidTokenError:
        return None
    return token


def generate_nonce():
    """
    Generate jti, it is a unique identified that is used to prevent the JWT from being replayed.
    :return:
    """
    return os.urandom(4).hex()
