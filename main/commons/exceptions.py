from typing import Optional

from flask import make_response

from main.schemas.exceptions import ErrorSchema


class StatusCode:
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    INTERNAL_SERVER_ERROR = 500


class _ErrorCode:
    # General error codes (xxx0xx)
    # Bad request error codes (4000xx)
    BAD_REQUEST = 400000
    VALIDATION_ERROR = 400001
    INVALID_AUTHORIZATION_HEADER = 400002

    # Unauthorized error codes (4010xx)
    UNAUTHORIZED = 401000
    INVALID_ACCESS_TOKEN = 401001
    EXPIRED_ACCESS_TOKEN = 401002
    FRESH_ACCESS_TOKEN_REQUIRED = 401003

    FORBIDDEN = 403000
    NOT_FOUND = 404000
    METHOD_NOT_ALLOWED = 405000
    INTERNAL_SERVER_ERROR = 500000


class _AccountErrorCode:
    # Member error codes (xxx1xx)
    # Unauthorized error codes (4011xx)
    INACTIVE_ACCOUNT = 401101
    ACCOUNT_NOT_FOUND = 401104


class _ErrorMessage:
    BAD_REQUEST = 'Bad request.'
    VALIDATION_ERROR = 'Validation error.'
    EMPTY_AUTHORIZATION_HEADER = 'Empty authorization header.'
    INVALID_AUTHORIZATION_HEADER = 'Authorization header should start with Bearer.'
    INVALID_ACCESS_TOKEN = 'Invalid access token.'
    EXPIRED_ACCESS_TOKEN = 'Expired access token.'
    FRESH_ACCESS_TOKEN_REQUIRED = 'Fresh access token is required.'
    UNAUTHORIZED = 'Unauthorized.'
    FORBIDDEN = 'Forbidden.'
    NOT_FOUND = 'Not found.'
    METHOD_NOT_ALLOWED = 'Method not allowed.'
    INTERNAL_SERVER_ERROR = 'Internal server error.'


class _AccountErrorMessage:
    # Account error messages
    INACTIVE_ACCOUNT = 'Inactive account.'
    ACCOUNT_NOT_FOUND = 'Account not found.'


class BaseError(Exception):
    def __init__(
        self,
        *,
        error_message=None,
        error_data=None,
        status_code: Optional[int] = None,
        error_code: Optional[int] = None,
    ):
        """
        Customize the response exception

        :param error_message: <string> Message field in the response body
        :param status_code: <number> HTTP status code
        :param error_data: <dict> Json body data
        :param error_code: <number> error code
        """
        if error_message is not None:
            self.error_message = error_message

        if status_code is not None:
            self.status_code = status_code

        if error_code is not None:
            self.error_code = error_code

        self.error_data = error_data

    def to_response(self):
        response = ErrorSchema().jsonify(self)

        return make_response(response, self.status_code)


class BadRequest(BaseError):
    status_code = StatusCode.BAD_REQUEST
    error_message = _ErrorMessage.BAD_REQUEST
    error_code = _ErrorCode.BAD_REQUEST


class ValidationError(BaseError):
    status_code = StatusCode.BAD_REQUEST
    error_message = _ErrorMessage.VALIDATION_ERROR
    error_code = _ErrorCode.VALIDATION_ERROR


class Unauthorized(BaseError):
    status_code = StatusCode.UNAUTHORIZED
    error_message = _ErrorMessage.UNAUTHORIZED
    error_code = _ErrorCode.UNAUTHORIZED


class Forbidden(BaseError):
    status_code = StatusCode.FORBIDDEN
    error_message = _ErrorMessage.FORBIDDEN
    error_code = _ErrorCode.FORBIDDEN


class NotFound(BaseError):
    status_code = StatusCode.NOT_FOUND
    error_message = _ErrorMessage.NOT_FOUND
    error_code = _ErrorCode.NOT_FOUND


class MethodNotAllowed(BaseError):
    status_code = StatusCode.METHOD_NOT_ALLOWED
    error_message = _ErrorMessage.METHOD_NOT_ALLOWED
    error_code = _ErrorCode.METHOD_NOT_ALLOWED


class InternalServerError(BaseError):
    status_code = StatusCode.INTERNAL_SERVER_ERROR
    error_message = _ErrorMessage.INTERNAL_SERVER_ERROR
    error_code = _ErrorCode.INTERNAL_SERVER_ERROR


class EmptyAuthorizationHeader(BaseError):
    status_code = StatusCode.BAD_REQUEST
    error_message = _ErrorMessage.EMPTY_AUTHORIZATION_HEADER
    error_code = _ErrorCode.INVALID_AUTHORIZATION_HEADER


class InvalidAuthorizationHeader(BaseError):
    status_code = StatusCode.BAD_REQUEST
    error_message = _ErrorMessage.INVALID_AUTHORIZATION_HEADER
    error_code = _ErrorCode.INVALID_AUTHORIZATION_HEADER


class ExpiredAccessToken(BaseError):
    status_code = StatusCode.UNAUTHORIZED
    error_message = _ErrorMessage.EXPIRED_ACCESS_TOKEN
    error_code = _ErrorCode.EXPIRED_ACCESS_TOKEN


class InvalidAccessToken(BaseError):
    status_code = StatusCode.UNAUTHORIZED
    error_message = _ErrorMessage.INVALID_ACCESS_TOKEN
    error_code = _ErrorCode.INVALID_ACCESS_TOKEN


class FreshAccessTokenRequired(BaseError):
    status_code = StatusCode.UNAUTHORIZED
    error_message = _ErrorMessage.FRESH_ACCESS_TOKEN_REQUIRED
    error_code = _ErrorCode.FRESH_ACCESS_TOKEN_REQUIRED


class InactiveAccount(BaseError):
    status_code = StatusCode.UNAUTHORIZED
    error_code = _AccountErrorCode.INACTIVE_ACCOUNT
    error_message = _AccountErrorMessage.INACTIVE_ACCOUNT


class AccountNotFound(BaseError):
    status_code = StatusCode.UNAUTHORIZED
    error_code = _AccountErrorCode.ACCOUNT_NOT_FOUND
    error_message = _AccountErrorMessage.ACCOUNT_NOT_FOUND
