class ConfigAPIException(Exception):
    def __init__(self, message, data=None):
        super(ConfigAPIException, self).__init__(message)
        self.message = message
        self.data = data

    def __str__(self):
        return '<{}> - {}'.format(self.__class__.__name__, self.message)


class TimeOutError(ConfigAPIException):
    pass


class ServiceError(ConfigAPIException):
    pass


class BadRequestError(ConfigAPIException):
    pass


class NotFoundError(ConfigAPIException):
    pass


class ForbiddenError(ConfigAPIException):
    pass


class InternalServerError(ConfigAPIException):
    pass


class ValidationNotFoundError(NotFoundError):
    pass


class ValidationUnfinishedError(BadRequestError):
    pass
