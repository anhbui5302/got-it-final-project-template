from main.libs.app_service import app_service

from .util import handle_exception, inject_project_url


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
    @inject_project_url
    def get_project(self, project_url):
        return self.application_service_client.make_request('get', project_url)

    @handle_exception
    @inject_project_url
    def get_autoflows(self, project_url):
        url = f'{project_url}/autoflows'
        return self.application_service_client.make_request('get', url)

    @handle_exception
    def get_autoflow(self, bot_type: str, *args, **kwargs):
        autoflows = self.get_autoflows(*args, **kwargs)
        return [autoflow for autoflow in autoflows if autoflow['bot_type'] == bot_type][
            0
        ]

    @handle_exception
    def get_all_projects(self, args: dict = None):
        url = f'{self.base_url}/projects'
        # Convert args['ids'] back into a string of comma-separated values from list
        if 'ids' in args.keys():
            args['ids'] = ','.join(args['ids'])

        return self.application_service_client.make_request('get', url, params=args)

    @handle_exception
    @inject_project_url
    def init_project_rasas(self, project_url, payload: dict):
        url = f'{project_url}/rasas'
        return self.application_service_client.make_request(
            'post', url, payload=payload
        )

    @handle_exception
    @inject_project_url
    def export_project_data(self, project_url, export_connections):
        url = f'{project_url}/export'
        payload = {'copy_connections': export_connections}
        return self.application_service_client.make_request(
            'post', url, payload=payload
        )

    @handle_exception
    @inject_project_url
    def import_project_data(self, project_url, file_tuple: tuple):
        url = f'{project_url}/import'
        files = {'files': file_tuple}
        return self.application_service_client.make_request('post', url, files=files)

    @handle_exception
    @inject_project_url
    def update_autoflow(self, project_url, autoflow_id: int, payload: dict = None):
        url = f'{project_url}/autoflows/{autoflow_id}'
        return self.application_service_client.make_request('put', url, payload=payload)
