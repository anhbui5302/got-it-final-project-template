from functools import wraps

from flask import request
from marshmallow import ValidationError

from main.commons import exceptions
from main.libs.log import ServiceLogger

logger = ServiceLogger(__name__)
NO_BODY_PARSING_METHODS = ['GET']


def get_request_args():
    if request.method == 'GET':
        return request.args.to_dict()
    return request.get_json() or {}


def parse_args_with(schema):
    """
    This decorator can be used to parse arguments of a request using a Marshmallow schema. If there is any validation
    error, a BadRequest exception will be raised along with the error details.
    """

    def parse_args_with_decorator(f):
        @wraps(f)
        def wrapper(**kwargs):
            request_args = get_request_args()
            try:
                parsed_args = schema.load(request_args)
            except ValidationError as exc:
                raise exceptions.ValidationError(error_data=exc.messages)
            kwargs['args'] = parsed_args
            return f(**kwargs)

        return wrapper

    return parse_args_with_decorator


def handle_config_api_exception(f):
    @wraps(f)
    def wrapper(**kwargs):
        from main.libs.config_api.exception import (
            BadRequestError,
            ConfigManagerException,
            NotFoundError,
        )

        try:
            return f(**kwargs)
        except BadRequestError as e:
            message = e.message or exceptions.ErrorMessage.BAD_REQUEST
            raise exceptions.BadRequest(error_message=message, error_data=e.data)
        except NotFoundError as e:
            message = e.message or exceptions.ErrorMessage.NOT_FOUND
            raise exceptions.NotFound(error_message=message, error_data=e.data)
        except ConfigManagerException as e:
            logger.exception(message=str(e))
            raise exceptions.InternalServerError()

    return wrapper
