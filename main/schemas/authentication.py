from marshmallow import fields, validate

from main.schemas.base import BaseSchema


class OAuthGoogleSchema(BaseSchema):
    id_token = fields.String(required=True)


class TokensRefreshingSchema(BaseSchema):
    refresh_token = fields.String(
        required=True, validate=validate.Length(min=1, max=255)
    )


class TokensRevokingSchema(BaseSchema):
    refresh_token = fields.String(
        required=True, validate=validate.Length(min=1, max=255)
    )
    access_token = fields.String(
        required=False, validate=validate.Length(min=1, max=255)
    )
