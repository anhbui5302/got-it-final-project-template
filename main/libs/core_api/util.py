from functools import wraps

import requests

from main.libs.app_service.exception import ApplicationServiceException

from .exception import (
    BadRequestError,
    CoreAPIException,
    ForbiddenError,
    InternalServerError,
    NotFoundError,
    ServiceError,
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
            error_message = error_data = None
            if e.data is not None:
                response_data = e.data.get('response')
                if response_data is None:
                    response_data = {}

                error_message = response_data.get('error_message', '')
                error_data = response_data.get('error_data', None)

            status_code = e.status_code
            if status_code == 400:
                raise BadRequestError(message=error_message, data=error_data)
            if status_code == 404:
                raise NotFoundError(message=error_message, data=error_data)
            if status_code == 403:
                raise ForbiddenError(message=error_message, data=error_data)
            if status_code == 500 and error_message:
                raise InternalServerError(message=error_message, data=error_data)

            raise CoreAPIException(message=error_message, data=e.data)

    return wrapper
