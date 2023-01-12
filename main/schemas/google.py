from marshmallow import fields, validate

from main.schemas.base import BaseSchema

ACCEPTED_ISSUERS = [
    'accounts.google.com',
    'https://accounts.google.com',
]


class GoogleUserInfoSchema(BaseSchema):
    aud = fields.String(required=True)
    iss = fields.String(required=True, validate=validate.OneOf(ACCEPTED_ISSUERS))
    email = fields.String(required=True, validate=validate.Email())
    sub = fields.String(required=True)
    name = fields.String(required=True)
