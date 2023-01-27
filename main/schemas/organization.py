from marshmallow import ValidationError, fields, pre_load, validate

from main.enums import OrganizationTier
from main.libs.log import ServiceLogger
from main.schemas.base import BaseSchema, PaginationSchema

logger = ServiceLogger(__name__)


class OrganizationBaseSchema(BaseSchema):
    id = fields.Integer()
    name = fields.String(dump_only=True)
    subdomain = fields.String()
    tier = fields.String()
    created = fields.String()
    updated = fields.String()


class OrganizationWithEmailSchema(OrganizationBaseSchema):
    account_email = fields.String()


class OrganizationsSchema(PaginationSchema):
    query = fields.String(load_only=True)
    ids = fields.List(fields.String(), load_only=True)
    tier = fields.String(load_only=True)

    @pre_load
    def load_ids(self, data, **__):
        if data.get('ids') is None:
            return data

        try:
            data['ids'] = data['ids'].split(',')
        except Exception as e:
            logger.error(message=str(e))
            raise ValidationError('Invalid ids parameters')

        return data


class ApplicationAdminCreationSchema(BaseSchema):
    tier = fields.String(
        required=True, validate=validate.OneOf(OrganizationTier.get_list())
    )
    account_email = fields.Email(required=True, validate=validate.Length(max=64))
    account_full_name = fields.String(
        required=True, validate=validate.Length(min=1, max=255)
    )
    account_password = fields.String(required=True)


class ApplicationAdminSchema(BaseSchema):
    id = fields.Integer()
    email = fields.Email()
    organization = fields.Nested(OrganizationBaseSchema)


class MemberTierUpdateSchema(BaseSchema):
    tier = fields.String(validate=validate.OneOf(OrganizationTier.get_list()))
