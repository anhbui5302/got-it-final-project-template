from savalidation import ValidationMixin, validators

from main import db
from main.enums import ApplicationStatus, AudienceType
from main.models.base import TimestampMixin


class ApplicationModel(db.Model, TimestampMixin, ValidationMixin):
    __tablename__ = 'application'
    audience_type = AudienceType.APPLICATION

    id = db.Column(db.Integer, primary_key=True)
    application_key = db.Column(db.String(255), nullable=False)
    application_secret = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255))
    status = db.Column(db.String(32), nullable=False, default=ApplicationStatus.ACTIVE)

    validators.validates_constraints()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
