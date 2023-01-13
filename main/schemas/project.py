from marshmallow import ValidationError, fields, pre_load, validate

from main.enums import ProjectRasaEnvironment
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


class ProjectInitRasaSchema(BaseSchema):
    environments = fields.List(
        fields.String(validate=validate.OneOf(ProjectRasaEnvironment.get_list())),
        required=True,
        validate=validate.Length(min=1, max=2),
    )


class RasaStatusChangedSchema(BaseSchema):
    project_id = fields.Integer(required=True)
    status = fields.String(required=True)
    env = fields.String(required=True)
