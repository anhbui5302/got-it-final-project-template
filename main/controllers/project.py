from flask import jsonify

from main import app, auth
from main.commons import exceptions
from main.core import (
    handle_config_api_exception,
    parse_args_with,
    parse_files_with,
    validate_project,
)
from main.engines.async_task import create_task
from main.engines.async_task.tasks.project import ExportProject
from main.engines.async_task.tasks.project.import_project import ImportProject
from main.engines.file import upload_file
from main.engines.project import generate_import_file_path
from main.enums import (
    BASE_PROJECT_PATH,
    AsyncTaskModule,
    AsyncTaskReferenceType,
    AsyncTaskStatus,
    FileReferenceType,
    FileType,
    ProjectImportFileName,
)
from main.libs.utils import get_config_api_sdk
from main.models.async_task import AsyncTaskMetaData, AsyncTaskModel
from main.schemas.project import (
    ProjectBaseSchema,
    ProjectExportSchema,
    ProjectImportFileSchema,
    ProjectInitRasaSchema,
    ProjectsSchema,
    ProjectTaskCreatedSchema,
)


@app.route('/projects', methods=['GET'])
@parse_args_with(ProjectsSchema())
@handle_config_api_exception
def get_projects(args, **__):
    """
    Get all projects list with filters
    :return:
    """
    config_api = get_config_api_sdk()
    response = config_api.get_all_projects(args)
    response['items'] = ProjectBaseSchema(many=True).dump(response['items'])

    return jsonify(response)


@app.route(f'{BASE_PROJECT_PATH}/rasas', methods=['POST'])
@validate_project
@parse_args_with(ProjectInitRasaSchema())
@handle_config_api_exception
def init_project_rasas_(organization_id: int, project_id: int, args, **__):
    config_api = get_config_api_sdk()
    response = config_api.init_project_rasas(organization_id, project_id, args)
    return jsonify(response)


@app.route(f'{BASE_PROJECT_PATH}/export', methods=['POST'])
@auth.require_account_token_auth()
@validate_project
@parse_args_with(ProjectExportSchema())
def create_export_project_task(project, account, args, **__):
    task = create_task(
        module=AsyncTaskModule.PROJECT,
        name=ExportProject.__name__,
        ref_type=AsyncTaskReferenceType.PROJECT,
        ref_id=project['id'],
        meta_data=AsyncTaskMetaData(
            kwargs={
                'account_id': account['id'],
                'project_id': project['id'],
                'organization_id': project['organization_id'],
                **args,
            }
        ),
        max_retry=0,
    )

    return ProjectTaskCreatedSchema().jsonify(task)


@app.route(f'{BASE_PROJECT_PATH}/import', methods=['POST'])
@auth.require_account_token_auth()
@validate_project
@parse_files_with(ProjectImportFileSchema())
def create_import_project_task(project, files, **__):
    # Check for pending/running tasks
    unfinished_async_task = AsyncTaskModel.query.filter(
        AsyncTaskModel.reference_type == AsyncTaskReferenceType.PROJECT,
        AsyncTaskModel.reference_id == 17,
        AsyncTaskModel.status.in_([AsyncTaskStatus.RUNNING, AsyncTaskStatus.PENDING]),
    ).first()
    if unfinished_async_task:
        raise exceptions.BadRequest(
            error_message=f'There are unfinished import tasks for project {project["id"]} running.'
        )

    # Upload file in request to S3
    zipped_file = files['files'][0]

    file = upload_file(
        reference_type=FileReferenceType.PROJECT,
        reference_id=project['id'],
        file_type=FileType.IMPORT,
        file_name=ProjectImportFileName.IMPORT,
        data=zipped_file.stream.read(),
        file_path=generate_import_file_path(
            project['id'], ProjectImportFileName.IMPORT
        ),
    )

    task = create_task(
        module=AsyncTaskModule.PROJECT,
        name=ImportProject.__name__,
        ref_type=AsyncTaskReferenceType.PROJECT,
        ref_id=project['id'],
        meta_data=AsyncTaskMetaData(
            kwargs={
                'project_id': project['id'],
                'organization_id': project['organization_id'],
                'file_url': file.url,
            }
        ),
        max_retry=0,
    )

    return ProjectTaskCreatedSchema().jsonify(task)
