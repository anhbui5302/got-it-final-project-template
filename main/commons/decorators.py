from functools import wraps
from typing import Type

import jwt
from flask import request
from jwt.exceptions import InvalidTokenError
from marshmallow import ValidationError
from werkzeug.exceptions import BadRequest

from main import config
from main.commons import exceptions
from main.schemas.base import BaseSchema


# Decorator to check if the user has provided the correct token to authenticate
# themselves.
def authentication(*, optional=False):
    def authentication_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get the token from the header.
            auth_header = request.headers.get("Authorization")
            # If login is optional and no authorization header is provided
            if optional and auth_header is None:
                return func(*args, **kwargs)
            # Validate the token
            # If no authorization header is provided
            if auth_header is None:
                raise exceptions.BadRequest(error_message="Missing header")
            # if token does not start with "Bearer " or length is smaller than 8
            # (i.e. it contains only "Bearer ")
            if (not auth_header.startswith("Bearer ")) or len(auth_header) < 8:
                raise exceptions.BadRequest(error_message="Malformed token.")

            access_token = auth_header.split(" ")[1]
            try:
                data = jwt.decode(
                    access_token, config.SECRET_KEY, ["HS256"], verify_signature=True
                )
                kwargs["user_id"] = data.get("id")
            except InvalidTokenError:
                # An exception is thrown when jwt cannot decode the token provided
                # (i.e. it is not correct). InvalidTokenError is the base exception when
                # decode() fails on a token. Others can be found on pyjwt's API page.
                raise exceptions.Unauthorized(error_message="Invalid or expired token.")
            return func(*args, **kwargs)

        return wrapper

    return authentication_decorator


def validate_request_body(*, schema_class: Type[BaseSchema]):
    def validate_request_body_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not issubclass(schema_class, BaseSchema):
                raise exceptions.InternalServerError(
                    error_message="Invalid param passed to validate body decorator."
                )

            try:
                request_data = request.get_json()
            except BadRequest:
                raise exceptions.BadRequest

            # Validate request data.
            try:
                validated_data = schema_class().load(request_data)
                kwargs["data"] = validated_data
            except ValidationError as err:
                raise exceptions.ValidationError(error_data=err.messages)
            return func(*args, **kwargs)

        return wrapper

    return validate_request_body_decorator


def validate_request_args(*, schema_class: Type[BaseSchema]):
    def validate_request_args_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not issubclass(schema_class, BaseSchema):
                raise exceptions.InternalServerError(
                    error_message="Invalid param passed to validate args decorator."
                )
            query_args = request.args

            # Validate request args.
            try:
                validated_args = schema_class().load(query_args)
                kwargs["query_args"] = validated_args
            except ValidationError as err:
                raise exceptions.ValidationError(error_data=err.messages)
            return func(*args, **kwargs)

        return wrapper

    return validate_request_args_decorator
