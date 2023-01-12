from main.libs.app_service import app_service

from .util import handle_exception


class ConfigAPI:
    def __init__(self, base_url, application_key, application_secret, **kwargs):
        """
        Args:
            base_url (str): The Config API URL
            application_key (str): The Core API Application Key
            application_secret (str): The Core API Application Secret
            **kwargs ():
                request_timeout (int): The request timeout
        """
        self.base_url = base_url
        self.application_service_client = app_service.ApplicationService(
            application_key, application_secret
        )
        self.request_timeout = kwargs.get('request_timeout', 10)  # seconds

    @handle_exception
    def get_all_projects(self, args: dict = None):
        url = f'{self.base_url}/projects'
        # Convert args['ids'] back into a string of comma-separated values from list
        if 'ids' in args.keys():
            args['ids'] = ','.join(args['ids'])

        return self.application_service_client.make_request('get', url, params=args)
