import json
from datetime import datetime
from typing import Dict

import attr

from main import db


class TimestampMixin:
    created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class MetaDataMixin:
    _meta_data_type = dict
    _meta_data = db.Column('meta_data', db.Text, nullable=True)

    @property
    def meta_data(self):
        try:
            raw_meta_data = json.loads(self._meta_data)
        except Exception:  # pragma: no cover
            raw_meta_data = {}

        return self._meta_data_type(**raw_meta_data)

    @meta_data.setter
    def meta_data(self, data):
        if not data:
            return

        if not isinstance(data, dict):
            data = attr.asdict(data)

        self._meta_data: Dict = json.dumps(data)
