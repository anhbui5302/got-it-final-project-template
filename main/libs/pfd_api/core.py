from main.libs.app_service import app_service

from .util import handle_exception


class PFDAPI:
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
    def get_sessions(self, project_id: int):
        url = f'{self.base_url}/sessions'
        params = {
            'project_id': project_id,
            'page': 1,
            'items_per_page': 1000,
        }
        return self.application_service_client.make_request('get', url, params=params)

    @handle_exception
    def export_session(self, session_id: int):
        url = f'{self.base_url}/sessions/{session_id}/export'
        return self.application_service_client.make_request('post', url)

    @handle_exception
    def import_session(self, session_id: int, file_tuple: tuple):
        url = f'{self.base_url}/sessions/{session_id}/import'
        files = {'files': file_tuple}
        return self.application_service_client.make_request('post', url, files=files)
