from flask import jsonify

from main import app
from main.core import handle_config_api_exception, parse_args_with
from main.libs.utils import get_config_api_sdk
from main.schemas.project import (
    ProjectBaseSchema,
    ProjectInitRasaSchema,
    ProjectsSchema,
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


@app.route(
    '/organizations/<int:organization_id>/projects/<int:project_id>/rasas',
    methods=['POST'],
)
@parse_args_with(ProjectInitRasaSchema())
@handle_config_api_exception
def init_project_rasas_(organization_id: int, project_id: int, args, **__):
    config_api = get_config_api_sdk()
    response = config_api.init_project_rasas(organization_id, project_id, args)
    return jsonify(response)
