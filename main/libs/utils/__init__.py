from main import config
from main.libs.config_api.core import ConfigAPI


def get_config_api_sdk() -> ConfigAPI:
    return ConfigAPI(
        base_url=config.CONFIG_API_BASE_URL,
        application_key=config.APPLICATION_KEY,
        application_secret=config.APPLICATION_SECRET,
        request_timeout=config.CONFIG_API_REQUEST_TIMEOUT,
    )
