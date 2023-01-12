from marshmallow import ValidationError, fields, pre_load

from main.libs.log import ServiceLogger
from main.schemas.base import BaseSchema, PaginationSchema

logger = ServiceLogger(__name__)


class ProjectBaseSchema(BaseSchema):
    id = fields.Integer()
    organization_id = fields.Integer()
    name = fields.String(dump_only=True)
    rasa_staging_status = fields.String()
    rasa_production_status = fields.String()


class ProjectsSchema(PaginationSchema):
    query = fields.String(load_only=True)
    ids = fields.List(fields.String(), load_only=True)

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
