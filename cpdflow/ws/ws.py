"""
Watson Studio APIs.
"""
import logging
import requests
from cpdflow.wml import wml

_logger = logging.getLogger(__name__)


def get_projects(config: dict) -> dict:
    """
    Get all projects.

    Args:
        config (dict): configuration dictionary
    
    Returns:
        dict: a dictionary of project names as keys and ids as values
    """
    wml_client = config["wml_client"]
    headers = {"Content-Type": "application/json", "Accept": "application/json", "Authorization": wml_client._get_headers()["Authorization"]}
    project_resources = requests.get("https://api.dataplatform.cloud.ibm.com/v2/projects", headers=headers).json()
    projects = {x["entity"]["name"]: x["metadata"]["guid"] for x in project_resources["resources"]}
    return projects


def store_model(config: dict, model_config: dict, log_format: str) -> None:
    """
    Store model in project space.

    Args:
        config (dict): configuration dictionary
        model_config (dict): model configuraton
        log_format (str): log format for this method
    """
    wml_client = config["wml_client"]
    facts_client = config["facts_client"]
    project_id = config["project_id"]
    wml_client.set.default_project(project_id)
    model_name = model_config["model_name"]
    model = model_config["model"]
    target = model_config["target"]
    input_data_schema = model_config["input_data_schema"]
    meta_props = {
        wml_client.repository.ModelMetaNames.NAME: model_name,
        wml_client.repository.ModelMetaNames.TYPE: "scikit-learn_1.0",
        wml_client.repository.ModelMetaNames.SOFTWARE_SPEC_UID: wml_client.software_specifications.get_uid_by_name("runtime-22.1-py3.9"),
        wml_client.repository.ModelMetaNames.LABEL_FIELD: target,
        wml_client.repository.ModelMetaNames.INPUT_DATA_SCHEMA: input_data_schema,
    }
    facts_client.export_facts.prepare_model_meta(wml_client=wml_client, meta_props=meta_props)
    wml_client.repository.store_model(model=model, meta_props=meta_props)
    _logger.info(f"{log_format} - store_model completed for {model_name}.")


def update_model(config: dict, model_config: dict, log_format: str) -> None:
    """
    Update model.

    Args:
        config (dict): configuration dictionary
        model_config (dict): model configuraton
        log_format (str): log format for this method
    """
    wml_client = config["wml_client"]
    project_id = config["project_id"]
    wml_client.set.default_project(project_id)

    model_name = model_config["model_name"]
    model = model_config["model"]
    models = wml.get_models(config=config, space_type="project")
    model_uid = models[model_name]
    updated_meta_props = {wml_client.repository.ModelMetaNames.NAME: model_name}
    wml_client.repository.update_model(model_uid, updated_meta_props=updated_meta_props, update_model=model)
    _logger.info(f"{log_format} - update_model completed for {model_name}.")


def delete_model_from_project_by_model_names(config: dict, model_names: list, log_format: str):
    """
    Delete model from project by model names

    Args:
        config (dict): configuration dictionary
        model_names (list[str]): model names
        log_format (str): log format for this method
    """
    wml.delete_model_by_model_names(config=config, model_names=model_names, space_type="project", log_format=log_format)
