class ConfigManagerException(Exception):
    def __init__(self, message, data=None):
        super(ConfigManagerException, self).__init__(message)
        self.message = message
        self.data = data

    def __str__(self):
        return '<{}> - {}'.format(self.__class__.__name__, self.message)


class TimeOutError(ConfigManagerException):
    pass


class ServiceError(ConfigManagerException):
    pass


class BadRequestError(ConfigManagerException):
    pass


class NotFoundError(ConfigManagerException):
    pass


class ForbiddenError(ConfigManagerException):
    pass


class InternalServerError(ConfigManagerException):
    pass


class ValidationNotFoundError(NotFoundError):
    pass


class ValidationUnfinishedError(BadRequestError):
    pass
