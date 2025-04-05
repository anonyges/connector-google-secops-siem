from google.oauth2 import service_account
from google.auth.transport import requests
import os

logger = get_logger(LOGGER_NAME)


class GoogleSecOpsSIEM(object):
    def __init__(self, config:dict, service_account_file_path: str):
        try:
            self.scopes = [
                "https://www.googleapis.com/auth/chronicle-backstory",
                "https://www.googleapis.com/auth/malachite-ingestion",
                "https://www.googleapis.com/auth/cloud-platform",
            ]
            # cert_file_iri = config.get("serviceAccountJSONFile", {}).get("@id")
            # filename = download_file_from_cyops(cert_file_iri).get("cyops_file_path")
            # file_data = os.path.join("/tmp", filename)
            credentials = service_account.Credentials.from_service_account_file(service_account_file_path, scopes=self.scopes)
            self.http_session = requests.AuthorizedSession(credentials)
        except Exception as e:
            logger.exception(f"{str(e)}")
            raise Exception(f"{str(e)}")

    def get_region_url(self, regionalEndpoint: str, apidoman: str):
        return "https://{0}-{1}.googleapis.com".format(regionalEndpoint, apidoman)

