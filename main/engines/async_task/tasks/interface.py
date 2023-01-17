from abc import ABC, abstractmethod
from typing import Any, Optional

from ..schemas import ExceptionInfo, Result


class AsyncTaskInterface(ABC):
    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def execute(self) -> Result:
        pass

    @abstractmethod
    def on_success(self, return_value: Optional[Any]):
        pass

    @abstractmethod
    def on_exception(self, e: ExceptionInfo):
        pass

    @abstractmethod
    def on_timed_out(self):
        pass

    @abstractmethod
    def retry(self):
        pass
