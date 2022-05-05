"""
Configuration utilities.
"""

import logging

import ibm_cloud_sdk_core
import ibm_watson_machine_learning
import ibm_watson_openscale
from ibm_aigov_facts_client import AIGovFactsClient

from cpdflow.ws import ws
from cpdflow.wml import wml
from cpdflow.wos import wos
from cpdflow.wkc import wkc

_logger = logging.getLogger(__name__)


def init_config(config: dict) -> dict:
    """
    Initialize configuration and return configuration dictionary.

    Refer to configuration link for configuration details.

    Args:
        configs (list[dict]): A list of dictionary with configurations for Cloud Pak for Data module

    Returns:
        dict: An initialize configuration dictionary
    """
    _logger.info("CONFIG - START")

    config_ = config.values()
    config = {}
    for x in config_:
        config.update(x)
    
    wml_credentials = {"apikey": config["apikey"], "url": config["url"]}
    wml_client = ibm_watson_machine_learning.APIClient(wml_credentials)
    wos_client = ibm_watson_openscale.APIClient(authenticator=ibm_cloud_sdk_core.authenticators.IAMAuthenticator(apikey=config["apikey"]))
    config.update({"wml_client": wml_client, "wos_client": wos_client})

    projects = ws.get_projects(config=config)
    config["project_id"] = projects[config["project_name"]]
    facts_client = AIGovFactsClient(api_key=config["apikey"], experiment_name="FactSheet Experiment", container_type="project", container_id=config["project_id"], set_as_current_experiment=True)
    config.update({"facts_client": facts_client})

    spaces = wml.get_spaces(config=config)
    if "dev_space" in config:
        config["dev_space_id"] = spaces[config["dev_space"]]
    if "prod_space" in config:
        config["prod_space_id"] = spaces[config["prod_space"]]
    service_providers = wos.get_service_providers(config=config)
    config["dev_service_provider_id"] = service_providers[config["dev_service_provider"]]
    config["prod_service_provider_id"] = service_providers[config["prod_service_provider"]]
    if "custom_service_provider" in config:
        config["custom_service_provider_id"] = service_providers[config["custom_service_provider"]]
    catalogs = wkc.get_catalogs(config=config)
    config["catalog_id"] = catalogs[config["catalog_name"]]
    _logger.info("CONFIG - COMPLETED")
    return config
