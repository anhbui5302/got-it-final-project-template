from functools import wraps

import requests

from main.libs.app_service.exception import ApplicationServiceException

from .exception import (
    BadRequestError,
    ConfigManagerException,
    ForbiddenError,
    InternalServerError,
    NotFoundError,
    ServiceError,
    TimeOutError,
    ValidationNotFoundError,
    ValidationUnfinishedError,
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
            error_message = error_data = error_code = None
            if e.data is not None:
                response_data = e.data.get('response')
                if response_data is None:
                    response_data = {}
                error_message = response_data.get('error_message', '')
                error_data = response_data.get('error_data', None)
                error_code = response_data.get('error_code', None)
            # Handle particular errors
            if error_code == 400200:
                raise ValidationUnfinishedError(message=error_message, data=error_data)
            if error_code == 404201:
                raise ValidationNotFoundError(message=error_message, data=error_data)

            # Handle generic errors
            status_code = e.status_code
            if status_code == 400:
                raise BadRequestError(message=error_message, data=error_data)
            if status_code == 404:
                raise NotFoundError(message=error_message, data=error_data)
            if status_code == 403:
                raise ForbiddenError(message=error_message, data=error_data)
            if status_code == 500 and error_message:
                raise InternalServerError(message=error_message, data=error_data)

            raise ConfigManagerException(message=str(e), data=e.data)

    return wrapper


def inject_project_url(f):
    @wraps(f)
    def wrapper(self, organization_id, project_id, *args, **kwargs):
        project_url = (
            f'{self.base_url}/organizations/{organization_id}/projects/{project_id}'
        )
        return f(self, project_url, *args, **kwargs)

    return wrapper
