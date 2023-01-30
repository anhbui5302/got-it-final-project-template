from savalidation import ValidationMixin, validators

from main import db
from main.enums import EventName
from main.models.base import MetaDataMixin, TimestampMixin


class EventModel(db.Model, TimestampMixin, ValidationMixin, MetaDataMixin):
    __tablename__ = 'event'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)

    validators.validates_constraints()
    validators.validates_one_of('name', EventName.get_list())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
