from datetime import datetime
from typing import Optional

from sqlalchemy import and_

from main import core, db
from main.enums import AsyncTaskStatus
from main.libs.log import ServiceLogger
from main.models.async_task import AsyncTaskMetaData, AsyncTaskModel

from .exceptions import AsyncTaskEngineException
from .factory import build_task

logger = ServiceLogger(__name__)


def create_task(
    module: str,
    name: str,
    root_id: Optional[int] = None,
    ref_type: Optional[str] = None,
    ref_id: Optional[int] = None,
    timeout: Optional[int] = None,
    meta_data: Optional[AsyncTaskMetaData] = None,
    max_retry: Optional[int] = None,
) -> AsyncTaskModel:
    """Create a task, then defer it to a queue."""
    logger.info(message='Creating async task', data=locals())
    task = AsyncTaskModel(
        module=module,
        name=name,
        root_id=root_id,
        reference_type=ref_type,
        reference_id=ref_id,
        timeout=timeout,
        meta_data=meta_data,
        max_retry=max_retry,
    )
    db.session.add(task)
    db.session.commit()

    # queue defer run_task
    # since we already handle retrying, max_retry should be set to 0
    core.queue_deferred(
        run_task,
        task_id=task.id,
        _max_retry=0,
        _key=str(ref_id) + ref_type if ref_id else None,
    )
    return task


def run_task(task_id: int):
    """Run a task by ID."""
    task: Optional[AsyncTaskModel] = AsyncTaskModel.query.get(task_id)
    if not task:
        raise AsyncTaskEngineException(message=f'Task ID {task_id} not found.')

    logger.info(message='Starting building and running a task.', data=task)
    task_ = build_task(task)
    task_.run()


def cleanup_expired_tasks():
    """Check if expiration_time has passed."""
    expired_tasks = (
        AsyncTaskModel.query.filter(
            and_(
                AsyncTaskModel.expiration_time < datetime.utcnow(),
                AsyncTaskModel.status.in_(
                    [AsyncTaskStatus.PENDING, AsyncTaskStatus.RUNNING]
                ),
            )
        )
        .order_by(AsyncTaskModel.id.asc())
        .all()
    )

    for expired_task in expired_tasks:
        task = build_task(expired_task)
        task.on_timed_out()
        task.notify_result()

    db.session.commit()
