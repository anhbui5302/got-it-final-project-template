from typing import List

from main.models.async_task import AsyncTaskModel

from .subscribers.interface import AsyncTaskSubscriberInterface


def send_notifications(
    subscribers: List[AsyncTaskSubscriberInterface], task: AsyncTaskModel
):
    for subscriber in subscribers:
        subscriber.notify(task)
