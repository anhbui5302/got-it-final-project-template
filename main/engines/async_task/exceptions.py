from typing import Optional


class AsyncTaskEngineException(Exception):
    def __init__(self, message: str, data: Optional[dict] = None):
        self.message = message
        self.data = data if data else {}

    def __str__(self):
        return '<{}, message={}, data={}>'.format(
            self.__class__.__name__, self.message, self.data
        )
