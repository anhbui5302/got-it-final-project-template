from main.libs.app_service import app_service

from .util import handle_exception


class CoreAPI:
    def __init__(self, base_url, application_key, application_secret, **kwargs):
        """
        Args:
            base_url (str): The Deepsearch API URL
            application_key (str): The Deepsearch API Application Key
            application_secret (str): The Deepsearch API Application Secret
            **kwargs ():
                request_timeout (int): The request timeout
        """
        self.base_url = base_url
        self.application_service_client = app_service.ApplicationService(
            application_key, application_secret
        )
        self.request_timeout = kwargs.get('request_timeout', 10)  # seconds

    @handle_exception
    def get_all_organizations(self, args=None):
        if args is None:
            args = {}
        url = f'{self.base_url}/organizations'
        # Convert args['ids'] back into a string of comma-separated values from list
        if 'ids' in args.keys():
            args['ids'] = ','.join(args['ids'])

        return self.application_service_client.make_request('get', url, params=args)

    @handle_exception
    def application_create_admin_member(self, payload: dict = None):
        url = f'{self.base_url}/application/admins'
        return self.application_service_client.make_request(
            'post', url, payload=payload
        )

    @handle_exception
    def change_organization_tier(self, organization_id: int, tier: str):
        payload = {'tier': tier}
        url = f'{self.base_url}/organizations/{organization_id}'
        return self.application_service_client.make_request('put', url, payload=payload)
