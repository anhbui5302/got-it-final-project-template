from .base import EnumBase


class TokenType(EnumBase):
    REFRESH_TOKEN = 'refresh_token'


class AccountStatus(EnumBase):
    DELETED = 'deleted'
    ACTIVE = 'active'


class AudienceType:
    ACCOUNT = 'account'
