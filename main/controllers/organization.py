from flask import jsonify

from main import app, auth
from main.commons import exceptions
from main.core import (
    handle_config_api_exception,
    handle_core_api_exception,
    parse_args_with,
)
from main.engines.event import create_event
from main.enums import EventName
from main.libs.utils import get_config_api_sdk, get_core_api_sdk
from main.schemas.organization import (
    ApplicationAdminCreationSchema,
    ApplicationAdminSchema,
    MemberTierUpdateSchema,
    OrganizationBaseSchema,
    OrganizationsSchema,
    OrganizationWithEmailSchema,
)
from main.schemas.project import ProjectBaseSchema


@app.route('/organizations', methods=['GET'])
@auth.require_account_token_auth()
@parse_args_with(OrganizationsSchema())
@handle_core_api_exception
def get_organizations(args, **__):
    """
    Get all organizations list with filters
    :return:
    """
    core_api = get_core_api_sdk()
    response = core_api.get_all_organizations(args)
    response['items'] = OrganizationWithEmailSchema(many=True).dump(response['items'])

    return jsonify(response)


@app.route('/application/admins', methods=['POST'])
@auth.require_account_token_auth()
@parse_args_with(ApplicationAdminCreationSchema())
@handle_core_api_exception
def application_create_admin_member(account, args: dict, **__):
    core_api = get_core_api_sdk()
    response = core_api.application_create_admin_member(args)

    event_meta_data = {
        'account_email': args['account_email'],
        'account_full_name': args['account_full_name'],
        'account_password': args['account_password'],
        'tier': args['tier'],
    }
    create_event(
        name=EventName.CREATE_ORGANIZATION,
        account_id=account.id,
        meta_data=event_meta_data,
    )
    return ApplicationAdminSchema().jsonify(response)


@app.route('/organizations/<int:organization_id>', methods=['PUT'])
@auth.require_account_token_auth()
@parse_args_with(MemberTierUpdateSchema())
@handle_core_api_exception
@handle_config_api_exception
def change_admin_member_tier(account, organization_id: int, args: dict, **__):
    tier = args.get('tier')
    # Assume admin member id is the same as organization id
    core_api = get_core_api_sdk()
    response = core_api.get_all_organizations(args={'ids': [str(organization_id)]})
    organizations = OrganizationWithEmailSchema(many=True).dump(response['items'])
    if not organizations:
        raise exceptions.BadRequest(
            error_message='Organization with the specified id do not exist.'
        )
    old_tier = organizations[0]['package']

    config_api = get_config_api_sdk()
    response = config_api.get_all_projects()
    projects = ProjectBaseSchema(many=True).dump(response['items'])
    try:
        project_id = [
            project['id']
            for project in projects
            if project['organization_id'] == organization_id
        ][0]
    except IndexError:
        raise exceptions.InternalServerError(
            error_message='Organization\'s project does not exist.'
        )

    change_organization_tier_response = core_api.change_organization_tier(
        organization_id, tier
    )
    config_api.change_autoflows_tier(organization_id, project_id, tier)

    organization = OrganizationBaseSchema().dump(change_organization_tier_response)
    response = {
        'id': organization['id'],
        'email': change_organization_tier_response['account_email'],
        'organization': organization,
    }

    event_meta_data = {
        'organization_id': organization_id,
        'old_tier': old_tier,
        'new_tier': tier,
    }
    create_event(
        name=EventName.CHANGE_TIER, account_id=account.id, meta_data=event_meta_data
    )
    return ApplicationAdminSchema().jsonify(response)
