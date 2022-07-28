from flask import jsonify
from marshmallow import EXCLUDE, Schema, fields, validate


class BaseSchema(Schema):
    class Meta:
        unknown = EXCLUDE
        ordered = True

    def jsonify(self, obj, many=False):
        return jsonify(self.dump(obj, many=many))


class PaginationSchema(BaseSchema):
    page = fields.Integer(validate=validate.Range(min=1), load_default=1)
    per_page = fields.Integer(validate=validate.Range(min=1), load_default=20)


class ItemPaginationSchema(PaginationSchema):
    category_id = fields.Integer(validate=validate.Range(min=1), load_default=None)


class TrimmedString(fields.String):
    def _deserialize(self, value, *args, **kwargs):
        if hasattr(value, "strip"):
            value = value.strip()
        return super()._deserialize(value, *args, **kwargs)
