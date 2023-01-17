from marshmallow import ValidationError, fields, pre_load, validate, validates_schema

from main.commons import exceptions
from main.enums import (
    AsyncTaskStatus,
    ProjectExportType,
    ProjectImportFileExtension,
    ProjectRasaEnvironment,
)
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


class ProjectExportSchema(BaseSchema):
    export = fields.List(
        fields.String(validate=validate.OneOf(ProjectExportType.get_list())),
        required=True,
    )
    export_connections = fields.Bool(missing=True)


def validate_value_empty(file):
    if file.filename == '':
        raise ValidationError('Missing data for required field.')


class ProjectImportFileSchema(BaseSchema):
    files = fields.List(
        fields.Field(validate=[validate_value_empty], required=True),
        required=True,
        validate=validate.Length(max=1),
    )

    @validates_schema
    def validate_file(self, data, *_, **__):
        error_data = {}
        valid_extensions = ProjectImportFileExtension.get_list()
        index = 0
        for key, file_list in data.items():
            for file in file_list:
                file_name = file.filename
                # Validate file keys
                if key != 'files':
                    error_data.update({index: ['Unsupported form data key.']})
                    raise exceptions.ValidationError(
                        error_message='Unsupported file key found. File key for all uploaded files '
                        'must be \'files\'.',
                        error_data={'files': error_data},
                    )
                # Validate file extensions
                elif file_name is None or not any(
                    file_name.lower().endswith(extension)
                    for extension in valid_extensions
                ):
                    error_data.update({index: ['Unsupported file extension.']})
                    raise exceptions.ValidationError(
                        error_message=f'Unsupported file extension found. Supported extensions are '
                        f'{valid_extensions}.',
                        error_data={'files': error_data},
                    )
                # Validate file name length
                elif len(file_name) > 255:
                    error_data.update({index: ['File name is too long.']})
                    raise exceptions.ValidationError(
                        error_message='File name is too long. File names must have at most 255 '
                        'characters.',
                        error_data={'files': error_data},
                    )
                elif file_name.split('.')[0] == '':
                    error_data.update({index: ['File name is too short.']})
                    raise exceptions.ValidationError(
                        error_message='File name is too short. File names must have at least 1 '
                        'character that is not part of the extension.',
                        error_data={'files': error_data},
                    )
                index += 1


class ProjectTaskCreatedSchema(BaseSchema):
    status = fields.String(
        required=True,
        validate=validate.OneOf(AsyncTaskStatus.get_list()),
    )
    id = fields.Integer(required=True)
