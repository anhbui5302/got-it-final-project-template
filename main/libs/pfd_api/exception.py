class PFDAPIException(Exception):
    def __init__(self, message, data=None):
        super().__init__(message)
        self.message = message
        self.data = data

    def __str__(self):
        return '<{}> - {}'.format(self.__class__.__name__, self.message)


class TimeOutError(PFDAPIException):
    pass


class ServiceError(PFDAPIException):
    pass


class StoriesAIConversationNotFound(PFDAPIException):
    pass


class SessionNotFound(PFDAPIException):
    pass


class ConversationNotInSession(PFDAPIException):
    pass


class ReportNotFound(PFDAPIException):
    pass


class InvalidSessionInputFile(PFDAPIException):
    pass


class BadRequestException(PFDAPIException):
    pass


class SelectedLabelsValidationError(PFDAPIException):
    pass


class StoriesAIValidationError(PFDAPIException):
    pass


class SessionNotInProject(PFDAPIException):
    pass
