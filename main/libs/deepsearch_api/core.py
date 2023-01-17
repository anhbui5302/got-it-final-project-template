from main.libs.app_service import app_service

from .util import handle_exception


class DeepsearchAPI:
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
    def export_project_graph(self, project_id, graph_id):
        url = f'{self.base_url}/projects/{project_id}/export'
        payload = {'graph_id': graph_id}
        return self.application_service_client.make_request(
            'post', url, payload=payload
        )

    @handle_exception
    def import_project_graph(self, project_id, file_tuple: tuple):
        url = f'{self.base_url}/projects/{project_id}/import'
        files = {'files': file_tuple}
        return self.application_service_client.make_request('post', url, files=files)
