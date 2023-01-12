import json

import jwt
import pytest

from main import db, jwttoken
from main.enums import AccountStatus
from main.libs.google_auth import GoogleAuthException
from main.models.account import AccountModel
from tests.helper import create_account, post_data

ACCOUNT_AUTH_ENDPOINT = '/access-tokens/google'
REFRESH_TOKEN_ENDPOINT = '/access-tokens/refresh'
REVOKE_TOKEN_ENDPOINT = '/access-tokens/revoke'


class TestAccountAuthentication:
    def _setup(self, session):
        self._account = create_account(session=session, email='*@bot-it.ai')

    @property
    def token(self):
        return jwttoken.encode(self._account)

    @property
    def account(self):
        return self._account

    @pytest.mark.parametrize(
        'email',
        ['abc@bot-it.ai', '*@bot-it.ai'],
    )
    def test_login_with_google_successfully(self, session, mocker, email):
        data = {'id_token': 'id_token'}
        mocker.patch(
            'main.controllers.authentication.get_google_user_info',
            return_value={
                'email': email,
                'google_id': 'google_id',
                'name': 'Name',
            },
        )

        response = post_data(
            token=None,
            url=ACCOUNT_AUTH_ENDPOINT,
            data=json.dumps(data),
        )
        assert response.status_code == 200
        assert 'access_token' in response.json
        assert 'refresh_token' in response.json
        decoded_data = jwt.decode(
            response.json['access_token'],
            options={'verify_signature': False},
        )
        assert decoded_data['fresh'] is True

    def test_fail_to_login_with_google(self, mocker):
        data = {'id_token': 'id_token'}
        mocker.patch(
            'main.controllers.authentication.get_google_user_info',
            side_effect=GoogleAuthException('Could not fetch google user information'),
        )

        response = post_data(
            token=None, url=ACCOUNT_AUTH_ENDPOINT, data=json.dumps(data)
        )
        assert response.status_code == 400

    def test_fail_to_login_with_google_with_inactive_account(self, mocker):
        data = {'id_token': 'id_token'}
        mocker.patch(
            'main.controllers.authentication.get_google_user_info',
            return_value={
                'email': '*@bot-it.ai',
                'google_id': 'google_id',
                'name': 'Name',
            },
        )
        account = AccountModel.query.filter(AccountModel.email == '*@bot-it.ai').first()
        account.status = AccountStatus.DELETED
        db.session.commit()

        response = post_data(
            token=None, url=ACCOUNT_AUTH_ENDPOINT, data=json.dumps(data)
        )
        assert response.status_code == 401
