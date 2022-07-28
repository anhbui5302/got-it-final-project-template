import logging


class BaseConfig:
    LOGGING_LEVEL = logging.INFO

    TOKEN_EXP_SECONDS = 300
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:12345678@127.0.0.1:3306/local"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False
    # SQLALCHEMY_ECHO = True
