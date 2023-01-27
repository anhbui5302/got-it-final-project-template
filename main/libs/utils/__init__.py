from main import config
from main.libs.config_api.core import ConfigAPI
from main.libs.core_api.core import CoreAPI
from main.libs.deepsearch_api.core import DeepsearchAPI
from main.libs.pfd_api.core import PFDAPI


def get_config_api_sdk() -> ConfigAPI:
    return ConfigAPI(
        base_url=config.CONFIG_API_BASE_URL,
        application_key=config.APPLICATION_KEY,
        application_secret=config.APPLICATION_SECRET,
        request_timeout=config.CONFIG_API_REQUEST_TIMEOUT,
    )


def get_deepsearch_api_sdk() -> DeepsearchAPI:
    return DeepsearchAPI(
        base_url=config.DEEPSEARCH_API_BASE_URL,
        application_key=config.DEEPSEARCH_API_APPLICATION_KEY,
        application_secret=config.DEEPSEARCH_API_APPLICATION_SECRET,
    )


def get_pfd_api_sdk() -> PFDAPI:
    return PFDAPI(
        base_url=config.PFD_API_BASE_URL,
        application_key=config.APPLICATION_KEY,
        application_secret=config.APPLICATION_SECRET,
        request_timeout=config.PFD_API_REQUEST_TIMEOUT,
    )


def get_core_api_sdk():
    return CoreAPI(
        base_url=config.CORE_API_URL,
        application_key=config.APPLICATION_KEY,
        application_secret=config.APPLICATION_SECRET,
    )
