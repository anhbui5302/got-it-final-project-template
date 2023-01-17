import traceback
from abc import ABC
from typing import Any, List, Optional

from main import db
from main.enums import AsyncTaskStatus
from main.libs.log import ServiceLogger
from main.models.async_task import AsyncTaskModel

from ..exceptions import AsyncTaskEngineException
from ..notification import send_notifications
from ..schemas import ExceptionInfo, Result
from .interface import AsyncTaskInterface

logger = ServiceLogger(__name__)


class BaseAsyncTask(AsyncTaskInterface, ABC):
    def __init__(self, task: AsyncTaskModel):
        self.task = task

    def run(self):
        """
        Check list
            - check status
            - change status to running
            - execute
            - handle error
            - notify result
        """
        if self.task.status != AsyncTaskStatus.PENDING:
            raise AsyncTaskEngineException(message='Task is not pending.')

        self.on_running()
        db.session.commit()

        try:
            result = self.execute()
        except Exception as e:
            exception_info = ExceptionInfo(
                exception=e,
                trace=traceback.format_exc(),
            )
            result = Result(exception_info=exception_info)

        if result.is_success:
            self.on_success(result.return_value)
        else:
            if result.is_errored:
                self.on_exception(result.exception_info)
            elif result.is_timed_out:
                self.on_timed_out()
            self.retry()
        db.session.commit()
        self.notify_result()

    def on_running(self):
        self.task.status = AsyncTaskStatus.RUNNING

    def on_success(self, _: Optional[Any]):
        # Log warning info if the task is not in RUNNING state
        if self.task.status != AsyncTaskStatus.RUNNING:
            warning_message = f'Task status = {self.task.status} ran successfully!'
            logger.warning(message=warning_message)
            exception_info = self.task.exception_info
            if exception_info.log:
                exception_info.log += warning_message
            else:
                exception_info.log = warning_message
            self.task.exception_info = exception_info
            return

        self.task.status = AsyncTaskStatus.SUCCESS
        logger.info(message=f'Ran task {self.task} successfully!')

    def on_exception(self, e: ExceptionInfo):
        # Only update status if the task is in RUNNING state
        if self.task.status == AsyncTaskStatus.RUNNING:
            self.task.status = AsyncTaskStatus.FAILED
        # Log exception
        self.task.exception = getattr(e.exception, 'message', str(e.exception))
        exception_info = self.task.exception_info
        exception_info.log = e.trace
        self.task.exception_info = exception_info
        logger.info(
            message=f'Exception occurred when running the task {self.task}.',
            data={'exception': e, 'traceback': e.trace},
        )

    def on_timed_out(self):
        self.task.status = AsyncTaskStatus.TIMED_OUT
        self.task.exception = (
            'Looks like the server is taking too long to respond, '
            'please try again later.'
        )
        logger.info(message=f'Task {self.task.id} is timed out.')

    def retry(self):
        if self.task.hit_max_retry:
            logger.info(message='Hit retry limit.', data={'task_id': self.task.id})
            return

        from .. import create_task

        create_task(
            module=self.task.module,
            name=self.task.name,
            root_id=self.task.get_root_id(),
            ref_type=self.task.reference_type,
            ref_id=self.task.reference_id,
            meta_data=self.task.meta_data,
            max_retry=(self.task.max_retry - 1),  # Decrease number of possible retries
        )

    def notify_result(self):
        if not (self.task.is_success or self.task.hit_max_retry):
            return

        from ..factory import build_subscribers

        # If this task ran successfully or already retried enough times but still
        # got exception/timed out, then notify the result to the other services if needed
        subscribers_name: List[str] = self.task.meta_data.subscribers
        subscribers = build_subscribers(subscribers_name)
        send_notifications(subscribers, self.task)
