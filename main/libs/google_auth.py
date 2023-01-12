# TODO: to be open sourced

from google.auth.exceptions import GoogleAuthError
from google.auth.transport import requests
from google.oauth2 import id_token
from marshmallow import ValidationError

from main.libs.log import ServiceLogger
from main.schemas.google import GoogleUserInfoSchema

logger = ServiceLogger(__name__)


class GoogleAuthException(Exception):
    def __init__(self, message, data=None):
        super().__init__(message)
        self.message = message
        self.data = data


def get_google_user_info(google_id_token: str, google_client_id: str):
    try:
        id_token_info = id_token.verify_oauth2_token(
            google_id_token, requests.Request(), google_client_id
        )
        id_token_info = GoogleUserInfoSchema().load(id_token_info)

        if id_token_info['aud'] != google_client_id:
            raise GoogleAuthException(
                'Failed to connect to Google. Please try it again.'
            )

        return {
            'email': id_token_info['email'],
            'google_id': id_token_info['sub'],
            'name': id_token_info['name'],
        }
    except GoogleAuthError as e:
        logger.error(message=f'Google Auth Exception: {e}')
        raise GoogleAuthException('Failed to connect to Google. Please try it again.')
    except ValidationError as e:
        logger.error(message=e.messages)
        raise GoogleAuthException(
            message='Unexpected user info data retrieved from Google.',
            data=e.messages,
        )
