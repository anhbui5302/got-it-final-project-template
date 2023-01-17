from typing import Any, Optional

import attr


@attr.s(auto_attribs=True)
class ExceptionInfo:
    exception: Exception
    trace: str


@attr.s(auto_attribs=True)
class Result:
    return_value: Optional[Any] = None

    is_timed_out: bool = False

    exception_info: Optional[ExceptionInfo] = None

    stdout: Optional[str] = None
    stderr: Optional[str] = None

    @property
    def is_errored(self) -> bool:
        return self.exception_info is not None

    @property
    def is_success(self) -> bool:
        return not self.is_errored and not self.is_timed_out
