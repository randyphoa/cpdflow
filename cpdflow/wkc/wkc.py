"""
Watson Knowledge Catalog APIs.
"""

import logging

import requests
from cpdflow.wml import wml

_logger = logging.getLogger(__name__)


def get_catalogs(config: dict) -> dict:
    """
    Get all catalogs.

    Args:
        config (dict): configuration dictionary
    
    Returns:
        dict: a dictionary of catalog names as keys and ids as values
    """
    wml_client = config["wml_client"]
    headers = {"Content-Type": "application/json", "Accept": "application/json", "Authorization": wml_client._get_headers()["Authorization"]}
    catalogs_resources = requests.get("https://api.dataplatform.cloud.ibm.com/v2/catalogs", headers=headers).json()
    catalogs = {x["entity"]["name"]: x["metadata"]["guid"] for x in catalogs_resources["catalogs"]}
    return catalogs


def get_model_entry_details(config: dict, space_type: str) -> dict:
    """
    Get all model entry details.

    Args:
        config (dict): configuration dictionary
        space_type (str): project, development or production environment
    
    Returns:
        dict: a dictionary of model entry detail names as keys and details as values
    """
    wml_client = config["wml_client"]
    catalog_id = config["catalog_id"]
    if space_type == "project":
        wml_client.set.default_project(config["project_id"])
    if space_type == "dev":
        wml_client.set.default_space(config["dev_space_id"])
    if space_type == "prod":
        wml_client.set.default_space(config["prod_space_id"])
    model_entry_details = {x["metadata"]["name"]: x for x in wml_client.factsheets.list_model_entries(catalog_id=catalog_id)["results"]}
    return model_entry_details


def get_model_entry_details_by_model_entry_name(config: dict, model_entry_name: str, space_type: str) -> dict:
    """
    Get model entry details by model entry name.

    Args:
        config (dict): configuration dictionary
        model_entry_name (str): model entry name
        space_type (str): project, development or production environment
        
    Returns:
        dict: model entry details
    """
    wml_client = config["wml_client"]
    catalog_id = config["catalog_id"]
    if space_type == "project":
        wml_client.set.default_project(config["project_id"])
    if space_type == "dev":
        wml_client.set.default_space(config["dev_space_id"])
    if space_type == "prod":
        wml_client.set.default_space(config["prod_space_id"])
    for x in wml_client.factsheets.list_model_entries(catalog_id=catalog_id)["results"]:
        if x and x["metadata"]["name"] == model_entry_name:
            return x


def delete_model_from_inventory_by_model_names(config: dict, model_names: list, space_type: str, log_format: str) -> None:
    """
    Delete models from inventory by model names.

    Args:
        config (dict): configuration dictionary
        model_names (list[str]): list of model names to be deleted from inventory
        space_type (str): development or production environment
        log_format (str): log format for this method
    """
    wml_client = config["wml_client"]
    if space_type == "project":
        container_id = config["project_id"]
        wml_client.set.default_project(config["project_id"])
    if space_type == "dev":
        container_id = config["dev_space_id"]
        wml_client.set.default_space(config["dev_space_id"])
    if space_type == "prod":
        container_id = config["prod_space_id"]
        wml_client.set.default_space(config["prod_space_id"])
    model_entry_name = config["model_entry_name"]
    model_entry_details = get_model_entry_details_by_model_entry_name(config=config, model_entry_name=model_entry_name, space_type=space_type)
    if model_entry_details:
        models = {x["name"]: x["id"] for x in model_entry_details["entity"]["modelfacts_global"]["physical_models"] if x["container_id"] == container_id and x["is_deleted"] == False}
        for x in model_names:
            if x in models:
                _logger.info(f"{log_format} - deleting ... {x}.")
                wml_client.factsheets.unregister_model_entry(asset_id=models[x])
                _logger.info(f"{log_format} - deleted {x}.")
    _logger.info(f"{log_format} - delete_model_from_inventory_by_model_names completed.")


def delete_model_from_project_inventory_by_model_names(config: dict, model_names: list, log_format: str):
    """
    Delete models from project inventory by model names.

    Args:
        config (dict): configuration dictionary
        model_names (list[str]): list of model names to be deleted from inventory
        log_format (str): log format for this method
    """
    delete_model_from_inventory_by_model_names(config=config, model_names=model_names, space_type="project", log_format=log_format)


def export_facts(config: dict, model_config: dict, log_format: str) -> None:
    """
    Export facts to Factsheets.

    Args:
        config (dict): configuration dictionary
        model_config (dict): model configuration
        log_format (str): log format for this method
    """
    wml_client = config["wml_client"]
    facts_client = config["facts_client"]
    project_id = config["project_id"]
    wml_client.set.default_project(project_id)
    custom_metrics = model_config["custom_metrics"]
    run_id = facts_client.runs.get_current_run_id()
    for key, value in custom_metrics.items():
        facts_client.runs.log_metric(run_id, key, value)
    facts_client.export_facts.export_payload(run_id)
    model_name = model_config["model_name"]
    _logger.info(f"{log_format} - exported_facts completed for {model_name}.")


def register_model_existing_entry(config: dict, model_uid: str, model_entry_asset_id: str, log_format: str) -> None:
    """
    Register model using an existing entry.

    Args:
        config (dict): configuration dictionary
        model_uid (str): model unique identifier
        model_entry_asset_id (str): model entry asset identifier
        log_format (str): log format for this method
    """
    wml_client = config["wml_client"]
    catalog_id = config["catalog_id"]
    meta_props = {
        wml_client.factsheets.ConfigurationMetaNames.ASSET_ID: model_entry_asset_id,
        wml_client.factsheets.ConfigurationMetaNames.MODEL_ENTRY_CATALOG_ID: catalog_id,
    }
    wml_client.factsheets.register_model_entry(model_id=model_uid, meta_props=meta_props)
    _logger.info(f"{log_format} - register_model_existing_entry completed.")


def register_model_new_entry(config: dict, model_uid: str, model_entry_name: str, model_entry_description: str, log_format: str) -> None:
    """
    Register model using a new entry.

    Args:
        config (dict): configuration dictionary
        model_entry_name (str): model entry name
        model_entry_description (str): model entry description
        log_format (str): log format for this method
    """
    wml_client = config["wml_client"]
    catalog_id = config["catalog_id"]
    wml_client.set.default_project(config["project_id"])
    meta_props = {
        wml_client.factsheets.ConfigurationMetaNames.NAME: model_entry_name,
        wml_client.factsheets.ConfigurationMetaNames.DESCRIPTION: model_entry_description,
        wml_client.factsheets.ConfigurationMetaNames.MODEL_ENTRY_CATALOG_ID: catalog_id,
    }
    wml_client.factsheets.register_model_entry(model_id=model_uid, meta_props=meta_props)
    _logger.info(f"{log_format} - register_model_new_entry completed.")


def register_model(config: dict, model_config: dict, space_type: str, log_format: str) -> None:
    """
    Register model.

    Args:
        config (dict): configuration dictionary
        model_config (dict): model configuration
        space_type (str): development or production environment
        log_format (str): log format for this method
    """
    model_name = model_config["model_name"]
    model_entry_name = config["model_entry_name"]
    model_entry_description = config["model_entry_description"]
    model_uid = wml.get_models(config=config, space_type=space_type)[model_name]
    model_entry_details = get_model_entry_details_by_model_entry_name(config=config, model_entry_name=model_entry_name, space_type=space_type)
    if model_entry_details:
        model_entry_asset_id = model_entry_details["metadata"]["asset_id"]
        register_model_existing_entry(config=config, model_uid=model_uid, model_entry_asset_id=model_entry_asset_id, log_format=log_format)
    else:
        register_model_new_entry(config=config, model_uid=model_uid, model_entry_name=model_entry_name, model_entry_description=model_entry_description, log_format=log_format)
    _logger.info(f"{log_format} - register_model completed for {model_name}.")


def register_model_from_project(config: dict, model_config: dict, log_format: str) -> None:
    """
    Register model from project

    Args:
        config (dict): configuration dictionary
        model_config (dict): model configuration
        log_format (str): log format for this method
    """
    register_model(config=config, model_config=model_config, space_type="project", log_format=log_format)

