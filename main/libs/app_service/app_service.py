from copy import deepcopy
from typing import Any, Iterator, Union

import requests

from main import application_jwttoken
from main.libs.utils.misc import mask_sensitive_information

from .exception import ApplicationServiceException


class ApplicationService:
    """
    Make HTTP requests to other services with JWT signature
    """

    def __init__(self, application_key, application_secret):
        """
        Args:
            application_key (str):
            application_secret (str):
        """
        self.application_key = application_key
        self.application_secret = application_secret

    def make_request(
        self,
        request_method,
        url,
        *,
        params=None,
        payload=None,
        timeout=None,
        on_success=None,
        on_failure=None,
        response_schema=None,
        headers=None,
        files=None,
        data=None,
        stream=False,
    ) -> Union[dict, Iterator[Any]]:
        """
        Make a HTTP request to a given service URL

        Args:
            request_method (str): The method of request
            url (str): The service URL
            params (dict): Parameters to be sent in the query string
            payload (any): Data to be sent in the request body as JSON
            timeout (int, optional): The request timeout
            on_success (function, optional): A callback function when the request succeeds
            on_failure (function, optional): A callback function when the request fails
            response_schema (Marshmallow, optional): A Marshmallow schema instance
            headers (optional): Request headers
            files (dict, optional): Upload file
            data (dict): Data to be sent in the request body
            stream (bool): Indicates whether the response should be received as stream
        Returns:
            The request response data
        Raises:
            app_service.exception.ApplicationServiceException if the request fails
        """
        authorization_token = application_jwttoken.encode(
            self.application_key, self.application_secret
        )
        headers_ = {'Authorization': 'Bearer {}'.format(authorization_token)}
        if headers:
            headers_.update(headers)

        response_body = None
        try:
            response = requests.request(
                request_method,
                url,
                params=params,
                json=payload,
                headers=headers_,
                timeout=timeout,
                files=files,
                data=data,
                stream=stream,
            )

            response_content_type = response.headers.get('Content-Type')
            if response_content_type is not None:
                if 'application/json' in response_content_type:
                    response_body = response.json()
                elif 'text/csv' in response_content_type:
                    response_body = response.content
                elif 'application/zip' in response_content_type:
                    response_body = response.content

            # Handle failure case
            if response.status_code != requests.codes.ok:
                masked_payload = deepcopy(payload)
                if masked_payload is not None:
                    masked_payload = mask_sensitive_information(
                        masked_payload, ['token']
                    )

                ApplicationService.raise_exception_from_status(
                    response.status_code,
                    'Error occurred when requesting to application service',
                    {
                        'url': url,
                        'payload': masked_payload,
                        'response': response_body,
                    },
                )
            # Validate the response if a schema was provided
            if response_schema is not None:
                response_schema.load(response_body)

            # Handle success case
            if on_success is not None:
                on_success(payload, response_body)

            if stream:
                return response.iter_content(chunk_size=1024)

            return response_body
        except Exception as exception:
            if on_failure is not None:
                on_failure(payload, response_body)

            raise exception

    @staticmethod
    def raise_exception_from_status(status_code, error_message, error_data):
        raise ApplicationServiceException(status_code, error_message, error_data)
