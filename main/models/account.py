from savalidation import ValidationMixin, validators
from sqlalchemy import Index

from main import db
from main.enums import AccountStatus, AudienceType
from main.models.base import TimestampMixin


class AccountModel(db.Model, TimestampMixin, ValidationMixin):
    __tablename__ = 'account'
    audience_type = AudienceType.ACCOUNT

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), nullable=True)
    status = db.Column(db.String(32), nullable=False, default=AccountStatus.ACTIVE)

    Index('idx_email', email)
    Index('idx_email_status', email, status, unique=True)

    validators.validates_constraints()
    validators.validates_one_of('status', AccountStatus.get_list())

    def __init__(self, *args, **kwargs):
        super(AccountModel, self).__init__(*args, **kwargs)
