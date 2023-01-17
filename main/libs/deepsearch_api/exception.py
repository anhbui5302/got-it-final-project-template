class DeepsearchAPIException(Exception):
    def __init__(self, message, data=None):
        super().__init__(message)

        self.message = message
        self.data = data

    def __str__(self):
        return '<{}> - {}'.format(self.__class__.__name__, self.message)


class TimeOutError(DeepsearchAPIException):
    pass


class ServiceError(DeepsearchAPIException):
    pass


class BadRequestError(DeepsearchAPIException):
    pass


class NotFoundError(DeepsearchAPIException):
    pass
