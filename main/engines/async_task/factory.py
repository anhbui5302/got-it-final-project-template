from importlib import import_module
from typing import List

from main.libs.log import ServiceLogger
from main.models.async_task import AsyncTaskModel

from .exceptions import AsyncTaskEngineException
from .subscribers.interface import AsyncTaskSubscriberInterface
from .tasks.base import BaseAsyncTask

TASKS_DIR_PATH = 'main.engines.async_task.tasks'
SUBSCRIBERS_DIR_PATH = 'main.engines.async_task.subscribers'
logger = ServiceLogger(__name__)


def build_task(task: AsyncTaskModel) -> BaseAsyncTask:
    module_name = f'{TASKS_DIR_PATH}.{task.module}'

    try:
        task_module = import_module(module_name)
    except ImportError as e:
        logger.exception(message=str(e))
        raise AsyncTaskEngineException(message='Cannot import module.')

    task_class = getattr(task_module, task.name)
    return task_class(task)


def build_subscriber(subscriber) -> AsyncTaskSubscriberInterface:
    """Build subscriber to receive task's result."""
    module_name = f'{SUBSCRIBERS_DIR_PATH}.{subscriber}'
    try:
        subscriber_module = import_module(module_name)
    except ImportError as e:
        logger.exception(message=str(e))
        raise AsyncTaskEngineException(message='Cannot import module.')

    subscriber_class_name = subscriber.title().replace('_', '')
    subscriber_class = getattr(subscriber_module, subscriber_class_name)
    return subscriber_class()


def build_subscribers(subscribers: List[str]) -> List[AsyncTaskSubscriberInterface]:
    return [build_subscriber(subscriber) for subscriber in subscribers]
