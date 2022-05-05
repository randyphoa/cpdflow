"""
Watson Machine Learning APIs.
"""

import logging
import requests
import time

_logger = logging.getLogger(__name__)


def get_spaces(config: dict) -> dict:
    """
    Get all spaces.

    Args:
        config (dict): configuration dictionary
    
    Returns:
        dict: a dictionary of space names as keys and ids as values
    """
    wml_client = config["wml_client"]
    href = wml_client.spaces._client.service_instance._href_definitions.get_platform_spaces_href()
    space_resources = wml_client.spaces._get_resources(href, "spaces", {})
    spaces = {x["entity"]["name"]: x["metadata"]["id"] for x in space_resources["resources"]}
    return spaces


def get_model_deployment_name(model_name: str) -> str:
    """
    Get model deployment name

    Args:
        model_name (str): model name
    
    Returns:
        str: model deployment name
    """
    return model_name + " Deployment"


def get_function_deployment_name(function_name: str) -> str:
    """
    Get function deployment name

    Args:
        function_name (str): function name
    
    Returns:
        str: function deployment name
    """
    return function_name + " Deployment"


def get_models(config: dict, space_type: str) -> dict:
    """
    Get all models.

    Args:
        config (dict): configuration dictionary
        space_type (str): project, development or production environment
    
    Returns:
        dict: a dictionary of model names as keys and ids as values
    """
    wml_client = config["wml_client"]
    if space_type == "project":
        wml_client.set.default_project(config["project_id"])
    if space_type == "dev":
        wml_client.set.default_space(config["dev_space_id"])
    if space_type == "prod":
        wml_client.set.default_space(config["prod_space_id"])
    models = {x["metadata"]["name"]: x["metadata"]["id"] for x in wml_client.repository.get_model_details()["resources"]}
    return models


def get_model_details(config: dict, space_type: str) -> dict:
    """
    Get all model details.

    Args:
        config (dict): configuration dictionary
        space_type (str): project, development or production environment
    
    Returns:
        dict: a dictionary of model names as keys and ids as values
    """
    wml_client = config["wml_client"]
    if space_type == "project":
        wml_client.set.default_project(config["project_id"])
    if space_type == "dev":
        wml_client.set.default_space(config["dev_space_id"])
    if space_type == "prod":
        wml_client.set.default_space(config["prod_space_id"])
    models = {x["metadata"]["name"]: x for x in wml_client.repository.get_model_details()["resources"]}
    return models


def get_functions(config: dict, space_type: str) -> dict:
    """
    Get all functions.

    Args:
        config (dict): configuration dictionary
        space_type (str): project, development or production environment
    
    Returns:
        dict: a dictionary of space names as keys and ids as values
    """
    wml_client = config["wml_client"]
    if space_type == "project":
        wml_client.set.default_project(config["project_id"])
    if space_type == "dev":
        wml_client.set.default_space(config["dev_space_id"])
    if space_type == "prod":
        wml_client.set.default_space(config["prod_space_id"])
    models = {x["metadata"]["name"]: x["metadata"]["id"] for x in wml_client.repository.get_function_details()["resources"]}
    return models


def get_deployment_details(config: dict, space_type: str) -> dict:
    """
    Get all deployments.

    Args:
        config (dict): configuration dictionary
        space_type (str): development or production environment
    
    Returns:
        dict: a dictionary of deployment names as keys and deployment details as values
    """
    wml_client = config["wml_client"]
    if space_type == "dev":
        wml_client.set.default_space(config["dev_space_id"])
    if space_type == "prod":
        wml_client.set.default_space(config["prod_space_id"])
    details = {x["metadata"]["name"]: x for x in wml_client.deployments.get_details()["resources"]}
    return details


def get_deployments(config: dict, space_type: str) -> dict:
    """
    Get all deployments.

    Args:
        config (dict): configuration dictionary
        space_type (str): development or production environment
    
    Returns:
        dict: a dictionary of deployment names as keys and ids as values
    """
    wml_client = config["wml_client"]
    if space_type == "dev":
        wml_client.set.default_space(config["dev_space_id"])
    if space_type == "prod":
        wml_client.set.default_space(config["prod_space_id"])
    models = {x["metadata"]["name"]: x["metadata"]["id"] for x in wml_client.deployments.get_details()["resources"]}
    return models


def check_model_stored(config: dict, model_name: str, log_format: str) -> bool:
    """
    Check if model exists in project space.

    Args:
        config (dict): configuration dictionary
        model_name (str): model name
        log_format (str): log format for this method

    Returns:
        bool: True if model exists in project space, otherwise False
    """
    models = get_models(config=config, space_type="project")
    is_stored = model_name in models
    _logger.info(f"{log_format} - check_model_stored - {is_stored} for {model_name}.")
    return is_stored


def check_model_promoted(config: dict, model_name: str, space_type: str, log_format: str) -> bool:
    """
    Check if model is promoted in given space.

    Args:
        config (dict): configuration dictionary
        model_name (str): model name
        space_type (str): development or production environment
        log_format (str): log format for this method
        
    Returns:
        bool: True if model exists in given space_type, otherwise False
    """
    models = get_models(config=config, space_type=space_type)
    is_promoted = model_name in models
    _logger.info(f"{log_format} - check_model_promoted - {is_promoted} for {model_name}.")
    return is_promoted


def check_model_deployed(config: dict, model_name: str, space_type: str, log_format: str) -> bool:
    """
    Check if model is deployed in given space.

    Args:
        config (dict): configuration dictionary
        model_name (str): model name
        space_type (str): development or production environment
        log_format (str): log format for this method
        
    Returns:
        bool: True if model is deployed in given space_type, otherwise False
    """
    deployments = get_deployments(config=config, space_type=space_type)
    is_deployed = get_model_deployment_name(model_name=model_name) in deployments
    _logger.info(f"{log_format} - check_model_deployed - {is_deployed} for {model_name}.")
    return is_deployed


def delete_model_by_model_names(config: dict, model_names: list, space_type: str, log_format: str) -> None:
    """
    Delete models by model names.

    Args:
        config (dict): configuration dictionary
        model_names (list[str]): list of model names to be deleted
        space_type (str): project, development or production environment
        log_format (str): log format for this method
    """

    wml_client = config["wml_client"]
    if space_type == "project":
        wml_client.set.default_project(config["project_id"])
    if space_type == "dev":
        wml_client.set.default_space(config["dev_space_id"])
    if space_type == "prod":
        wml_client.set.default_space(config["prod_space_id"])

    models = get_models(config=config, space_type=space_type)
    for x in model_names:
        if x in models:
            _logger.info(f"{log_format} - deleting ... {x}.")
            wml_client.repository.delete(models[x])
            _logger.info(f"{log_format} - deleted {x}.")
    _logger.info(f"{log_format} - delete_model_by_model_names completed.")


def delete_model_deployment_by_model_deployment_names(config: dict, model_deployment_names: list, space_type: str, log_format: str) -> None:
    """
    Delete model deployments by model deployment names.

    Args:
        config (dict): configuration dictionary
        model_deployment_names (list[str]): list of model deployment names to be deleted
        space_type (str): project, development or production environment
        log_format (str): log format for this method
    """

    wml_client = config["wml_client"]
    if space_type == "dev":
        wml_client.set.default_space(config["dev_space_id"])
    if space_type == "prod":
        wml_client.set.default_space(config["prod_space_id"])

    deployments = get_deployments(config=config, space_type=space_type)
    for x in model_deployment_names:
        if x in deployments:
            _logger.info(f"{log_format} - deleting ... {x}.")
            wml_client.deployments.delete(deployments[x])
            _logger.info(f"{log_format} - deleted {x}.")
    _logger.info(f"{log_format} - delete_model_deployment_by_model_deployment_names completed.")


def delete_function_by_function_names(config: dict, function_names: list, space_type: str, log_format: str) -> None:
    """
    Delete functions by functions names.

    Args:
        config (dict): configuration dictionary
        function_names (list[str]): list of functions to be deleted
        space_type (str): project, development or production environment
        log_format (str): log format for this method
    """

    wml_client = config["wml_client"]
    if space_type == "project":
        wml_client.set.default_project(config["project_id"])
    if space_type == "dev":
        wml_client.set.default_space(config["dev_space_id"])
    if space_type == "prod":
        wml_client.set.default_space(config["prod_space_id"])

    functions = get_functions(config=config, space_type=space_type)
    for x in function_names:
        if x in functions:
            wml_client.repository.delete(functions[x])
            _logger.info(f"{log_format} - delete_function_by_function_names completed for {x}.")


def delete_function_deployment_by_function_deployment_names(config: dict, function_deployment_names: list, space_type: str) -> None:
    """
    Delete function deployments by function deployment names.

    Args:
        config (dict): configuration dictionary
        function_deployment_names (list[str]): list of function deployment names to be deleted
        space_type (str): development or production environment
        log_format (str): log format for this method
    """

    wml_client = config["wml_client"]
    if space_type == "dev":
        wml_client.set.default_space(config["dev_space_id"])
    if space_type == "prod":
        wml_client.set.default_space(config["prod_space_id"])

    deployments = get_deployments(config=config, space_type=space_type)
    for x in function_deployment_names:
        if x in deployments:
            wml_client.deployments.delete(deployments[x])


def promote_model(config: dict, model_name: str, space_type: str, log_format: str) -> None:
    """"
    Promote model in given space.

    Args:
        config (dict): configuration dictionary
        model_name (str): model name
        space_type (str): development or production environment
        log_format (str): log format for this method
    """
    _logger.info(f"{log_format} - promoting model ... {model_name}.")
    wml_client = config["wml_client"]
    space_id = config["dev_space_id"] if space_type == "dev" else config["prod_space_id"]
    model_uid = get_models(config=config, space_type="project")[model_name]
    # model_uid = wml.get_model_uid_by_model_name(config=config, model_name=model_name, space_type="project")
    headers = {"Content-Type": "application/json", "Accept": "application/json", "Authorization": wml_client._get_headers()["Authorization"]}
    params = {"project_id": config["project_id"]}
    data = {"mode": 0, "space_id": space_id}
    requests.post(f"https://api.dataplatform.cloud.ibm.com/v2/assets/{model_uid}/promote", headers=headers, params=params, json=data)
    _logger.info(f"{log_format} - promote_model completed for {model_name}.")


def deploy_model(config: dict, model_name: str, space_type: str, log_format: str) -> None:
    """"
    Deploy model in given space.

    Args:
        config (dict): configuration dictionary
        model_name (str): model name
        space_type (str): development or production environment
        log_format (str): log format for this method
    """
    _logger.info(f"{log_format} - deploying model ... {model_name}.")
    wml_client = config["wml_client"]
    space_id = config["dev_space_id"] if space_type == "dev" else config["prod_space_id"]
    wml_client.set.default_space(space_id)
    deployment_name = get_model_deployment_name(model_name=model_name)
    model_uid = get_models(config=config, space_type=space_type)[model_name]
    meta_props = {wml_client.deployments.ConfigurationMetaNames.NAME: deployment_name, wml_client.deployments.ConfigurationMetaNames.ONLINE: {}}
    wml_client.deployments.create(model_uid, meta_props=meta_props)
    _logger.info(f"{log_format} - deploy_model completed for {model_name}.")


def update_deployed_model(config: dict, model_name: str, space_type: str, log_format: str) -> None:
    """"
    Update model in given space.

    Args:
        config (dict): configuration dictionary
        model_name (str): model name
        space_type (str): development or production environment
        log_format (str): log format for this method
    """
    _logger.info(f"{log_format} - updating deployed model ... {model_name}.")
    wml_client = config["wml_client"]
    space_id = config["dev_space_id"] if space_type == "dev" else config["prod_space_id"]
    wml_client.set.default_space(space_id)
    models = get_models(config=config, space_type=space_type)
    model_uid = models[model_name]
    deployment_name = get_model_deployment_name(model_name=model_name)
    deployments = get_deployments(config=config, space_type=space_type)
    deployment_uid = deployments[deployment_name]
    changes = {wml_client.deployments.ConfigurationMetaNames.ASSET: {"id": model_uid}}
    wml_client.deployments.update(deployment_uid, changes=changes)
    _logger.info(f"{log_format} - updated_deploy_model completed for {model_name}.")


def deploy_function(config: dict, function: callable, function_name: str, space_type: str) -> None:
    """"
    Deploy function in given space.

    Args:
        config (dict): configuration dictionary
        function (callable): function to be deployed
        function_name (str): function name
        space_type (str): development or production environment
    """
    wml_client = config["wml_client"]
    space_id = config["dev_space_id"] if space_type == "dev" else config["prod_space_id"]
    wml_client.set.default_space(space_id)
    function_deployment_name = get_function_deployment_name(function_name)
    delete_function_deployment_by_function_deployment_names(config=config, function_deployment_names=[function_deployment_name], space_type=space_type)
    delete_function_by_function_names(config=config, function_names=[function_name], space_type=space_type, log_format="")
    meta_props = {
        wml_client.repository.FunctionMetaNames.NAME: function_name,
        wml_client.repository.FunctionMetaNames.SOFTWARE_SPEC_ID: wml_client.software_specifications.get_uid_by_name("runtime-22.1-py3.9"),
    }
    function_details = wml_client.repository.store_function(function=function, meta_props=meta_props)
    function_uid = wml_client.repository.get_function_id(function_details)
    meta_props = {
        wml_client.deployments.ConfigurationMetaNames.NAME: function_deployment_name,
        wml_client.deployments.ConfigurationMetaNames.ONLINE: {},
        wml_client.deployments.ConfigurationMetaNames.HARDWARE_SPEC: {"id": wml_client.hardware_specifications.get_id_by_name("M")},
    }
    wml_client.deployments.create(function_uid, meta_props=meta_props)


def score_model(config: dict, model_name: str, scoring_payload: dict, space_type: str, log_format: str) -> None:
    """"
    Score model in given space with scoring payload

    Args:
        config (dict): configuration dictionary
        model_name (str): model name
        scoring_payload (dict): scoring payload
        space_type (str): development or production environment
        log_format (str): log format for this method
    """
    _logger.info(f"{log_format} - scoring model ... {model_name}.")
    wml_client = config["wml_client"]
    deployment_name = get_model_deployment_name(model_name=model_name)
    model_deployments = get_deployments(config=config, space_type=space_type)
    deployment_uid = model_deployments[deployment_name]
    wml_client.deployments.score(deployment_uid, scoring_payload)
    time.sleep(5)
    _logger.info(f"{log_format} - score_model completed for {model_name}.")
