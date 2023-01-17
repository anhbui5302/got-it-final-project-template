import datetime

from savalidation import validators
from sqlalchemy import Index

from main import config, db
from main.enums import FileReferenceType, FileType
from main.models.base import TimestampMixin


def calculate_expiration_time():
    return datetime.datetime.utcnow() + datetime.timedelta(
        seconds=config.UPLOADED_FILE_EXPIRATION_IN_SECONDS
    )


class FileModel(db.Model, TimestampMixin):
    __tablename__ = 'file'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    url = db.Column(db.String(1024), nullable=False)
    type = db.Column(db.String(64), nullable=False)
    reference_type = db.Column(db.String(64), nullable=False)
    reference_id = db.Column(db.Integer)

    validators.validates_one_of('type', FileType.get_list())
    validators.validates_one_of('reference_type', FileReferenceType.get_list())

    Index('idx_file_ref_type_ref_id', reference_type, reference_id)

    expiration_time = db.Column(
        db.DateTime, default=calculate_expiration_time, nullable=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
