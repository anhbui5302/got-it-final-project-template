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

    # EVENT BUS
    EVENT_BUS_URL = 'http://localhost:4000/api/produce'
    EVENT_BUS_DELAYED_URL = 'http://localhost:4000/api/produce_delayed'
    API_SERVER = 'http://localhost:8060'
    EVENT_BUS_PARTITIONS = 100

    APPLICATION_KEY = 'admin_panel_api_application_key'
    APPLICATION_SECRET = 'admin_panel_api_application_secret'

    CONFIG_API_BASE_URL = 'http://localhost:5000'
    CONFIG_API_APPLICATION_KEY = 'config_manager_application_key'
    CONFIG_API_APPLICATION_SECRET = 'config_manager_application_secret'
    CONFIG_API_REQUEST_TIMEOUT = 300
