from connectors.core.connector import Connector
from connectors.core.connector import get_logger, ConnectorError
from django.utils.module_loading import import_string
from connectors.cyops_utilities.builtins import download_file_from_cyops
from .constants import LOGGER_NAME

import json, os
from datetime import datetime, timedelta
from custom_connector import GoogleSecOpsSIEM

logger = get_logger(LOGGER_NAME)


class BaseConnector(Connector):
    def execute(self, config: dict, operation: str, params: dict, *args, **kwargs):
        return supported_operations.get(operation)(config, params)

    def check_health(self, config: dict = None, *args, **kwargs):
        return check_health(config, *args, **kwargs)


def get_service_account_file_path(config: dict) -> str:
    cert_file_iri = config.get("serviceAccountJSONFile", {}).get("@id")
    filename = download_file_from_cyops(cert_file_iri).get("cyops_file_path")
    return os.path.join("/tmp", filename)


def check_health(config: dict, params: dict = None):
    try:
        client_obj = GoogleSecOpsSIEM(config, get_service_account_file_path(config))
        url = (
            client_obj.get_region_url(config.get("regionalEndpoint"), "chronicle")
            + f'/v1alpha/projects/{config.get("projectID")}/locations/{config.get("regionalEndpoint")}/instances/{config.get("instanceID")}/legacy:legacyFetchAlertsView'
        )
        startTime = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")
        endTime = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        payload = {"alertListOptions.maxReturnedAlerts": 1, "timeRange.startTime": startTime, "timeRange.endTime": endTime}
        response = client_obj.http_session.request("GET", url, params=payload)
        if response.status_code == 200:
            return response.json()
        raise ConnectorError("{0}".format(str(response.content)))
    except Exception as err:
        logger.exception("{0}".format(str(err)))
        raise ConnectorError("{0}".format(str(err)))


def execute_api_endpoint(config, params):
    try:
        client_obj = GoogleSecOpsSIEM(config, get_service_account_file_path(config))
        url = client_obj.get_region_url(config.get("regionalEndpoint"), params.get("apidomain")) + params.get("api_endpoint")
        method = params.get("method")
        payload = json.loads(params.get("params")) if isinstance(params.get("params"), str) else params.get("params", dict())
        payload = {k: v for k, v in payload.items() if v is not None and v != ""} if isinstance(payload, dict) else None
        data = params.get("data")
        response = client_obj.http_session.request(method, url, params=payload, data=data)
        if response.status_code == 200:
            return response.json()
        raise ConnectorError("{0}".format(str(response.content)))
    except Exception as err:
        logger.exception("{0}".format(str(err)))
        raise ConnectorError("{0}".format(str(err)))


def legacyfetchalertsview(config, params):
    try:
        client_obj = GoogleSecOpsSIEM(config, get_service_account_file_path(config))
        url = (
            client_obj.get_region_url(config.get("regionalEndpoint"), "chronicle")
            + f'/v1alpha/projects/{config.get("projectID")}/locations/{config.get("regionalEndpoint")}/instances/{config.get("instanceID")}/legacy:legacyFetchAlertsView'
        )
        method = "GET"
        payload = {
            "baselineQuery": params.get("baselineQuery", None),
            "alertListOptions.maxReturnedAlerts": params.get("alertListOptionsMaxReturnedAlerts", 100),
            "timeRange.startTime": params.get("timeRangeStartTime"),
            "timeRange.endTime": params.get("timeRangeEndTime"),
        }
        payload = {k: v for k, v in payload.items() if v is not None and v != ""} if isinstance(payload, dict) else None
        response = client_obj.http_session.request(method, url, params=payload)
        if response.status_code == 200:
            return response.json()[-1]
        raise ConnectorError("{0}".format(str(response.content)))
    except Exception as err:
        logger.exception("{0}".format(str(err)))
        raise ConnectorError("{0}".format(str(err)))


def legacygetalert(config, params):
    try:
        client_obj = GoogleSecOpsSIEM(config, get_service_account_file_path(config))
        url = (
            client_obj.get_region_url(config.get("regionalEndpoint"), "chronicle")
            + f'/v1alpha/projects/{config.get("projectID")}/locations/{config.get("regionalEndpoint")}/instances/{config.get("instanceID")}/legacy:legacyGetAlert'
        )
        method = "GET"
        payload = {
            "alertId": params.get("alertId", None),
            "includeDetections": params.get("includeDetections", False),
        }
        payload = {k: v for k, v in payload.items() if v is not None and v != ""} if isinstance(payload, dict) else None
        response = client_obj.http_session.request(method, url, params=payload)
        if response.status_code == 200:
            return response.json()
        raise ConnectorError("{0}".format(str(response.content)))
    except Exception as err:
        logger.exception("{0}".format(str(err)))
        raise ConnectorError("{0}".format(str(err)))


def udm_search(config, params):
    try:
        client_obj = GoogleSecOpsSIEM(config, get_service_account_file_path(config))
        url = client_obj.get_region_url(config.get("regionalEndpoint"), "backstory") + f'/v1/{params.get("udm_type")}:udmSearch'
        payload = {
            "query": params.get("query"),
            "time_range.start_time": params.get("time_range.start_time"),
            "time_range.end_time": params.get("time_range.end_time"),
            "limit": params.get("limit"),
        }
        payload = {k: v for k, v in payload.items() if v is not None and v != ""}
        response = client_obj.http_session.request("GET", url, params=payload)
        if response.status_code == 200:
            return response.json()
        raise ConnectorError("{0}".format(str(response.content)))
    except Exception as err:
        logger.exception("{0}".format(str(err)))
        raise ConnectorError("{0}".format(str(err)))


supported_operations = {
    "health_check": check_health,
    "execute_api_endpoint": execute_api_endpoint,
    "legacyfetchalertsview": legacyfetchalertsview,
    "legacygetalert": legacygetalert,
    "udm_search": udm_search,
}
