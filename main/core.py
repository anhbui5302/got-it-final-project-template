import base64
import os
import random
from functools import wraps

from flask import g, has_request_context, request
from marshmallow import ValidationError

from main import config, event_bus
from main.commons import exceptions
from main.commons.exceptions import ErrorCode, ErrorMessage
from main.delayed_deferred import defer
from main.libs.log import ServiceLogger
from main.libs.utils import get_config_api_sdk

logger = ServiceLogger(__name__)
NO_BODY_PARSING_METHODS = ['GET']


def queue_deferred(*args, **kwargs):
    if has_request_context():
        queue_deferred_after_request(*args, **kwargs)
    else:
        queue_deferred_eventbus(*args, **kwargs)


def queue_deferred_after_request(*args, **kwargs):
    # On test environment, queue should not run
    if os.getenv('ENVIRONMENT', 'development') == 'test':
        return None

    task = _build_event_bus_task(*args, **kwargs)
    # Put the task in the task list from application context (different for each request) and execute the list when
    # the request is finished
    delayed_tasks = getattr(g, 'delayed_tasks', [])
    delayed_tasks.append(task)
    g.delayed_tasks = delayed_tasks


def queue_deferred_eventbus(*args, **kwargs):
    # On test environment, queue should not run
    if os.getenv('ENVIRONMENT', 'development') == 'test':
        return None

    task = _build_event_bus_task(*args, **kwargs)
    event_bus.send_task(task)


def _build_event_bus_task(*args, **kwargs):
    reserved_args = [
        'countdown',
        'eta',
        'name',
        'target',
        'queue',
        'retry_options',
        'key',
        'max_retry',
        'timeout',
    ]
    taskargs = dict((x, kwargs.pop(('_%s' % x), None)) for x in reserved_args)
    queue = taskargs.get('queue', None)
    func = args[0]
    url = '/_ah/eb_queue/deferred_flask'
    if hasattr(func, '__name__'):
        url = url + '/{}'.format(func.__name__)
    taskargs['_url'] = url
    payload = defer(*args, **kwargs)

    key = taskargs.get('key', None)
    if key is None:
        key = random.randint(0, config.EVENT_BUS_PARTITIONS)

    task = {
        'payload': base64.encodestring(payload).decode(),
        'topic': queue,
        'key': str(key),
        'url': config.API_SERVER + url,
    }
    max_retry = taskargs.get('max_retry', None)
    if max_retry is not None:
        task['max_retry'] = max_retry
    timeout = taskargs.get('timeout', None)
    if timeout:
        task['timeout'] = timeout

    countdown = taskargs.get('countdown', None)
    if countdown:
        task['delay'] = str(countdown * 1000)
    return task


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


def parse_files_with(schema):
    def parse_request_files_with_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            request_files = request.files.to_dict(flat=False)
            try:
                parsed_files = schema.load(request_files)
            except ValidationError as e:
                raise exceptions.ValidationError(error_data=e.messages)

            kwargs['files'] = parsed_files
            return f(*args, **kwargs)

        return wrapper

    return parse_request_files_with_decorator


def validate_project(f):
    @wraps(f)
    @handle_config_api_exception
    def wrapper(organization_id, project_id, **kwargs):
        config_api = get_config_api_sdk()
        response = config_api.get_project(organization_id, project_id)
        kwargs['project'] = response
        return f(**kwargs)

    return wrapper


def handle_config_api_exception(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        from main.libs.config_api.exception import (
            BadRequestError,
            ConfigManagerException,
            NotFoundError,
        )

        try:
            return f(*args, **kwargs)
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


def handle_deepsearch_api_exception(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        from main.libs.deepsearch_api.exception import (
            BadRequestError,
            DeepsearchAPIException,
            NotFoundError,
        )

        try:
            return f(*args, **kwargs)
        except BadRequestError as e:
            message = e.message or exceptions.ErrorMessage.BAD_REQUEST
            raise exceptions.BadRequest(error_message=message, error_data=e.data)
        except NotFoundError as e:
            message = e.message or exceptions.ErrorMessage.NOT_FOUND
            raise exceptions.NotFound(error_message=message, error_data=e.data)
        except DeepsearchAPIException as e:
            logger.exception(message=str(e))
            raise exceptions.InternalServerError()

    return wrapper


def handle_pfd_api_exception(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        from main.libs.pfd_api.exception import (
            BadRequestException,
            ConversationNotInSession,
            InvalidSessionInputFile,
            PFDAPIException,
            ReportNotFound,
            SelectedLabelsValidationError,
            SessionNotFound,
            SessionNotInProject,
            StoriesAIConversationNotFound,
            StoriesAIValidationError,
        )

        try:
            return f(*args, **kwargs)
        except SessionNotInProject:
            raise exceptions.BadRequest(
                error_code=ErrorCode.SESSION_NOT_IN_PROJECT,
                error_message=ErrorMessage.SESSION_NOT_IN_PROJECT,
            )
        except SessionNotFound:
            raise exceptions.NotFound(
                error_code=ErrorCode.SESSION_NOT_FOUND,
                error_message=ErrorMessage.SESSION_NOT_FOUND,
            )
        except ReportNotFound:
            raise exceptions.NotFound(
                error_code=ErrorCode.REPORT_NOT_FOUND,
                error_message=ErrorMessage.REPORT_NOT_FOUND,
            )
        except ConversationNotInSession:
            raise exceptions.BadRequest(
                error_code=ErrorCode.CONVERSATION_NOT_IN_SESSION,
                error_message=ErrorMessage.CONVERSATION_NOT_IN_SESSION,
            )
        except StoriesAIConversationNotFound:
            raise exceptions.NotFound(
                error_code=ErrorCode.CONVERSATION_NOT_FOUND,
                error_message=ErrorMessage.CONVERSATION_NOT_FOUND,
            )
        except SelectedLabelsValidationError as e:
            raise exceptions.BadRequest(
                error_code=ErrorCode.SELECTED_LABELS_VALIDATION_ERROR,
                error_message=e.message,
            )
        except StoriesAIValidationError as e:
            raise exceptions.ValidationError(error_data=e.data)
        except (BadRequestException, InvalidSessionInputFile) as e:
            message = e.message or ErrorMessage.BAD_REQUEST
            raise exceptions.BadRequest(error_message=message, error_data=e.data)
        except PFDAPIException as e:
            logger.exception(message=str(e))
            raise exceptions.InternalServerError()

    return wrapper
