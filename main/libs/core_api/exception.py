class CoreAPIException(Exception):
    def __init__(self, message, data=None):
        super().__init__(message)

        self.message = message
        self.data = data

    def __str__(self):
        return '<{}> - {}'.format(self.__class__.__name__, self.message)


class TimeOutError(CoreAPIException):
    pass


class ServiceError(CoreAPIException):
    pass


class BadRequestError(CoreAPIException):
    pass


class NotFoundError(CoreAPIException):
    pass


class ForbiddenError(CoreAPIException):
    pass


class InternalServerError(CoreAPIException):
    pass
