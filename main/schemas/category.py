from marshmallow import fields, validate

from main.schemas.base import BaseSchema, TrimmedString


class CategorySchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    name = TrimmedString(required=True, validate=validate.Length(min=1, max=255))
    user_id = fields.Integer(load_only=True)  # Don't want user_id to be dumped
    is_owner = fields.Method("determine_ownership")
    created = fields.Str(dump_only=True)
    updated = fields.Str(dump_only=True)

    def determine_ownership(self, obj):
        if self.context["authenticated_user_id"] == obj.user_id:
            return True
        return False
