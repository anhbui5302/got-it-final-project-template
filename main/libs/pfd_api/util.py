from functools import wraps

import requests

from main.commons.exceptions import ErrorCode
from main.libs.app_service.exception import ApplicationServiceException

from .exception import (
    BadRequestException,
    ConversationNotInSession,
    InvalidSessionInputFile,
    PFDAPIException,
    ReportNotFound,
    SelectedLabelsValidationError,
    ServiceError,
    SessionNotFound,
    SessionNotInProject,
    StoriesAIConversationNotFound,
    StoriesAIValidationError,
    TimeOutError,
)


def handle_exception(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except requests.exceptions.Timeout as e:
            raise TimeOutError(str(e))
        except requests.exceptions.RequestException as e:
            raise ServiceError((str(e)))
        except ApplicationServiceException as e:
            response = e.data['response'] or {}
            error_code = response.get('error_code')
            error_message = response.get('error_message')
            error_data = response.get('error_data')

            if error_code == ErrorCode.CONVERSATION_NOT_FOUND:
                raise StoriesAIConversationNotFound(message=error_message, data=e.data)

            if error_code == ErrorCode.SESSION_NOT_FOUND:
                raise SessionNotFound(message=error_message, data=e.data)

            if error_code == ErrorCode.CONVERSATION_NOT_IN_SESSION:
                raise ConversationNotInSession(message=error_message, data=e.data)

            if error_code == ErrorCode.SESSION_NOT_IN_PROJECT:
                raise SessionNotInProject(message=error_message, data=e.data)

            if error_code == ErrorCode.REPORT_NOT_FOUND:
                raise ReportNotFound(message=error_message, data=e.data)

            if error_code == ErrorCode.INVALID_SESSION_FILE_INPUT:
                raise InvalidSessionInputFile(message=error_message, data=error_data)

            if error_code == ErrorCode.BAD_REQUEST:
                raise BadRequestException(message=error_message, data=error_data)

            if error_code == ErrorCode.SELECTED_LABELS_VALIDATION_ERROR:
                raise SelectedLabelsValidationError(message=error_message, data=e.data)

            if error_code == ErrorCode.VALIDATION_ERROR:
                raise StoriesAIValidationError(
                    message=error_message,
                    data=error_data,
                )

            raise PFDAPIException(message=error_message, data=e.data)

    return wrapper
