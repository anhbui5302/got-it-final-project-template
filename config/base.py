import logging


class BaseConfig:
    DEBUG = True
    TESTING = False
    JWT_SECRET = ''
    ACCESS_TOKEN_LIFETIME = 600  # 10 minutes
    LOGGING_SERVICE_LOG_LEVEL = logging.DEBUG

    SQLALCHEMY_DATABASE_URI = (
        'mysql+pymysql://root:123456@127.0.0.1/admin_panel_development'
    )
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_MAX_OVERFLOW = 0
    SQLALCHEMY_POOL_SIZE = 10
    SQLALCHEMY_RECORD_QUERIES = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    GOOGLE_CLIENT_ID = ''

    ALLOWED_DOMAINS = ['bot-it.ai']
    REFRESH_TOKEN_EXPIRATION_TIMEOUT = 1 * 60 * 60 * 24  # 1 day
