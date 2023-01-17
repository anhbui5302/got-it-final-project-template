from abc import ABC, abstractmethod

from main.models.async_task import AsyncTaskModel


class AsyncTaskSubscriberInterface(ABC):
    @abstractmethod
    def notify(self, task: AsyncTaskModel):
        pass
