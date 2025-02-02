from connectors.core.connector import Connector
from connectors.core.connector import get_logger, ConnectorError
from django.utils.module_loading import import_string
from .constants import LOGGER_NAME
from .operations import supported_operations

logger = get_logger(LOGGER_NAME)


class CustomConnector(Connector):

    def execute(self, config:dict, operation: str, params: dict, *args, **kwargs):
        return supported_operations.get(operation)(config, params)

    def check_health(self, config=None, *args, **kwargs):
        return True
