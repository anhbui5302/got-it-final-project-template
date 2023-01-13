from .base import EnumBase


class TokenType(EnumBase):
    REFRESH_TOKEN = 'refresh_token'


class AccountStatus(EnumBase):
    DELETED = 'deleted'
    ACTIVE = 'active'


class AudienceType:
    ACCOUNT = 'account'
    APPLICATION = 'application'


class ProjectRasaEnvironment(EnumBase):
    STAGING = 'staging'
    PRODUCTION = 'production'


class ApplicationStatus(EnumBase):
    DELETED = 'deleted'
    ACTIVE = 'active'


class PusherEvent:
    RASA_STATUS_CHANGED = 'project_rasa_status_changed'
