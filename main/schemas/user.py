from marshmallow import ValidationError, fields, validate

from main.schemas.base import BaseSchema


def validate_password(password):
    # Checks if password has the required length, has at least one digit, uppercase and
    # lowercase letter.
    error_data = []
    if not (5 < len(password) < 33):
        # raise ValidationError("Length must be between 6 and 32.")
        error_data.append("Length must be between 6 and 32.")
    if not any(char.isdigit() for char in password):
        # raise ValidationError("Missing digit.")
        error_data.append("Missing digit.")
    if not any(char.isupper() for char in password):
        # raise ValidationError("Missing uppercase letter.")
        error_data.append("Missing uppercase letter.")
    if not any(char.islower() for char in password):
        # raise ValidationError("Missing lowercase letter.")
        error_data.append("Missing lowercase letter.")
    if error_data:
        raise ValidationError(error_data)


class UserSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    email = fields.Email(required=True, validate=validate.Length(min=3, max=254))
    password = fields.Str(required=True, load_only=True, validate=validate_password)
    created = fields.Str(dump_only=True)
    updated = fields.Str(dump_only=True)
