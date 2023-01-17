import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import attr
from savalidation import validators

from main import config, db
from main.enums import AsyncTaskReferenceType, AsyncTaskStatus
from main.models.base import MetaDataMixin, TimestampMixin

# The maximum number that a task can be retried
MAX_RETRY = config.ASYNC_TASK_MAX_RETRY
EXPIRATION_TIMEOUT = config.ASYNC_TASK_EXPIRATION_TIMEOUT


def get_expiration_timeout(t: timedelta) -> datetime:
    return datetime.utcnow() + t


def get_default_expiration_timeout() -> datetime:
    return get_expiration_timeout(timedelta(seconds=EXPIRATION_TIMEOUT))


@attr.s(auto_attribs=True)
class AsyncTaskMetaData:
    args: List = attr.ib(factory=list)
    kwargs: Dict = attr.ib(factory=dict)
    data: Dict = attr.ib(factory=dict)
    subscribers: List[str] = attr.ib(factory=list)


@attr.s(auto_attribs=True)
class ExceptionInfo:
    log: Optional[str] = attr.ib(default=None)
    data: Optional[dict] = attr.ib(default=None)


class AsyncTaskModel(db.Model, TimestampMixin, MetaDataMixin):
    __tablename__ = 'async_task'

    id = db.Column(db.Integer, primary_key=True)
    root_id = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(32), nullable=False, default=AsyncTaskStatus.PENDING)
    module = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    exception = db.Column(db.Text, nullable=True)  # Exception message
    _exception_info = db.Column(
        'exception_info',
        db.Text,
        nullable=True,
    )  # Exception data and trace back
    max_retry = db.Column(db.Integer, nullable=False, default=MAX_RETRY)
    expiration_time = db.Column(
        db.DateTime, nullable=False, default=get_default_expiration_timeout
    )
    reference_type = db.Column(db.String(255), nullable=True)
    reference_id = db.Column(db.Integer, nullable=True)
    _meta_data_type = AsyncTaskMetaData

    validators.validates_one_of('state', AsyncTaskStatus.get_list())
    validators.validates_one_of('reference_type', AsyncTaskReferenceType.get_list())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f'id={self.id}, module={self.module}, name={self.name}'

    @property
    def exception_info(self) -> ExceptionInfo:
        try:
            raw_exception_info = json.loads(self._exception_info)
        except Exception:  # pragma: no cover
            raw_exception_info = {}
        return ExceptionInfo(**raw_exception_info)

    @exception_info.setter
    def exception_info(self, data):
        if not data:
            return
        if not isinstance(data, dict):
            data = attr.asdict(data)
        self._exception_info = json.dumps(data)

    @property
    def timeout(self) -> float:
        return (self.expiration_time - self.created).total_seconds()

    @timeout.setter
    def timeout(self, seconds: int):
        if not isinstance(seconds, int):
            return
        self.expiration_time = get_expiration_timeout(timedelta(seconds=seconds))

    def get_root_id(self):
        if self.root_id:
            return self.root_id
        return self.id

    @property
    def hit_max_retry(self):
        return self.max_retry == 0

    @property
    def is_success(self):
        return self.status == AsyncTaskStatus.SUCCESS

    @property
    def data(self):
        return self.meta_data.data
