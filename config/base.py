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

    MEMCACHED_SERVERS = ['127.0.0.1:11211']
    MEMCACHED_KEY_PREFIX = 'stories-ai-api:m345:'

    DISKCACHE_DIRECTORY = '~/.cache/diskcache'
    DISKCACHE_SIZE_LIMIT = 2**30  # 1GB

    # EVENT BUS
    EVENT_BUS_URL = 'http://localhost:4000/api/produce'
    EVENT_BUS_DELAYED_URL = 'http://localhost:4000/api/produce_delayed'
    API_SERVER = 'http://localhost:8060'
    EVENT_BUS_PARTITIONS = 100

    # PUSHER
    PUSHER_APP_ID = '711154'
    PUSHER_CHANNEL_NAMESPACE = 'admin_panel'
    PUSHER_KEY = ''
    PUSHER_SECRET = ''

    # AWS
    AWS_ACCESS_KEY_ID = ''
    AWS_SECRET_ACCESS_KEY = ''
    AWS_FILE_PATH_PREFIX = ''
    AWS_S3_BUCKET_NAME = ''
    AWS_S3_URL = ''

    APPLICATION_KEY = ''
    APPLICATION_SECRET = ''

    # CONFIG API
    CONFIG_API_BASE_URL = 'http://localhost:5000'
    CONFIG_API_APPLICATION_KEY = ''
    CONFIG_API_APPLICATION_SECRET = ''
    CONFIG_API_REQUEST_TIMEOUT = 300

    # DEEPSEARCH API
    DEEPSEARCH_API_BASE_URL = 'http://localhost:8090'
    DEEPSEARCH_API_APPLICATION_KEY = ''
    DEEPSEARCH_API_APPLICATION_SECRET = ''

    # PFD API
    PFD_API_BASE_URL = 'http://localhost:8091'
    PFD_API_REQUEST_TIMEOUT = 2 * 60 * 60  # seconds

    # CORE API
    CORE_API_URL = ''

    ASYNC_TASK_MAX_RETRY = 0
    ASYNC_TASK_EXPIRATION_TIMEOUT = 30  # seconds

    UPLOADED_FILE_EXPIRATION_IN_SECONDS = 5 * 60  # seconds
