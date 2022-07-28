from .local import Config as _Config


class Config(_Config):
    TESTING = True
    SECRET_KEY = "testing"
    TOKEN_EXP_SECONDS = 10

    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:12345678@127.0.0.1:3306/test"
