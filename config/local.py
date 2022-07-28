from .base import BaseConfig


class Config(BaseConfig):
    DEBUG = True
    SECRET_KEY = "local"
    TESTING = False
    JSONIFY_PRETTYPRINT_REGULAR = False
