import uuid
from datetime import datetime, timedelta

from savalidation import ValidationMixin, validators
from sqlalchemy import Index

from main import config, db
from main.enums import TokenType
from main.models.base import TimestampMixin


def generate_expiration_time() -> datetime:
    return datetime.utcnow() + timedelta(
        seconds=config.REFRESH_TOKEN_EXPIRATION_TIMEOUT
    )


def generate_token_value() -> str:
    return str(uuid.uuid4())


class TokenModel(db.Model, TimestampMixin, ValidationMixin):
    __tablename__ = 'token'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    type = db.Column(db.String(32), nullable=False)
    expiration_time = db.Column(
        db.DateTime, nullable=False, default=generate_expiration_time
    )
    value = db.Column(
        db.String(64), unique=True, nullable=False, default=generate_token_value
    )

    account = db.relationship('AccountModel', foreign_keys=[account_id])

    validators.validates_one_of('type', TokenType.get_list())
    Index('idx_token_value', value)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def is_expired(self) -> bool:
        return self.expiration_time <= datetime.utcnow()
