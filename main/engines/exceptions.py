from typing import Optional


class BaseEngineException(Exception):
    def __init__(
        self,
        message: str,
        data: Optional[dict] = None,
    ):
        self.message = message
        self.data = data

    def __str__(self):
        return '<{}, message={}, data={}>'.format(
            self.__class__.__name__, self.message, self.data
        )


class AccountException(BaseEngineException):
    pass


class TokenException(BaseEngineException):
    pass
