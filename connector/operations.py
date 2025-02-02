from connectors.core.connector import get_logger, ConnectorError
from .utils import invoke_rest_endpoint
from .constants import LOGGER_NAME
from connectors.cyops_utilities.builtins import download_file_from_cyops
from google.oauth2 import service_account
from google.auth.transport import requests
import json
import os

logger = get_logger(LOGGER_NAME)


class GoogleSecOpsSIEM(object):
    def __init__(self, config):
        try:
            self.scopes = ["https://www.googleapis.com/auth/chronicle-backstory"]
            cert_file_iri = config.get("serviceAccountJSONFile", {}).get("@id")
            filename = download_file_from_cyops(cert_file_iri).get("cyops_file_path")
            file_data = os.path.join("/tmp", filename)
            credentials = service_account.Credentials.from_service_account_file(file_data, scopes=self.scopes)
            self.http_session = requests.AuthorizedSession(credentials)
        except Exception as err:
            logger.exception("{0}".format(str(err)))
            raise ConnectorError("{0}".format(str(err)))


def execute_api_endpoint(config, params):
    try:
        client_obj = GoogleSecOpsSIEM(config)
        url = "https://{0}{1}".format(config.get("regionalEndpoint"), params.get("api_endpoint"))
        method = params.get("method")
        payload = json.loads(params.get("parameters")) if isinstance(params.get("parameters"), str) else params.get("parameters")
        payload = {k: v for k, v in payload.items() if v is not None and v != ""}
        response = client_obj.http_session.request(method, url, params=payload)
        if response:
            return response.json()
    except Exception as err:
        logger.exception("{0}".format(str(err)))
        raise ConnectorError("{0}".format(str(err)))


supported_operations = {'execute_api_endpoint': execute_api_endpoint, }
