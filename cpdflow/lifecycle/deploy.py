"""
Promotes and deploys model to the specified environment.
"""
import logging
import importlib
from cpdflow import graph
from cpdflow.wml import wml
from cpdflow.wos import wos

_logger = logging.getLogger(__name__)


def deploy_remove(config: dict, model_configs: list, space_type: str, backward_steps: list) -> None:
    """
    Remove deployments that are specified in ``model_configs``.

    Args:
        config (dict): configuration dictionary
        model_configs (list[dict]): models to be removed
        space_type (str): development or production environment
        backward_steps (list[str]): list of steps to remove downstream assets
    """
    all_models = wml.get_models(config=config, space_type=space_type)
    model_names = [x["model_name"] for x in model_configs]
    delete_models = [x for x in all_models.keys() if x in model_names]
    if delete_models:
        log_format = f"DEPLOY - {'REMOVE':<15} - backward_steps"
        _logger.info(f"{log_format} - {' -> '.join(backward_steps)} for {model_names}")
        graph.remove(config=config, model_names=delete_models, space_types=[space_type], backward_steps=backward_steps, log_format=log_format)
    else:
        _logger.info(f"DEPLOY - {'REMOVE':<15} - Nothing to remove")


def deploy_update(config: dict, model_configs: list, space_type: str) -> None:
    """
    Update deployments that are specified in ``model_configs``.

    Args:
        config (dict): configuration dictionary
        model_configs (list[dict]): models to be updated
        space_type (str): development or production environment
    """
    deployments = wml.get_deployments(config=config, space_type=space_type)
    model_configs = [x for x in model_configs if x["update"] and wml.get_model_deployment_name(model_name=x["model_name"]) in deployments]
    if model_configs:
        for model_config in model_configs:
            model_name = model_config["model_name"]
            log_format = f"DEPLOY - {'UPDATE':<15} - update_steps"
            _logger.info(f"{log_format} - update_deployed_model for {model_name}")
            wml.update_deployed_model(config=config, model_name=model_name, space_type=space_type, log_format=log_format)
    else:
        _logger.info(f"DEVELOP - {'UPDATE':<15} - Nothing to update.")


def deploy_overwrite(config: dict, model_configs: list, space_type: str, backward_steps: list):
    """
    Overwrite deployments that are specified in ``model_configs``.

    Args:
        config (dict): configuration dictionary
        model_configs (list[dict]): models to be removed
        space_type (str): development or production environment
        backward_steps (list[str]): list of steps to remove downstream assets
    """
    if model_configs:
        model_names = [x["model_name"] for x in model_configs if x["overwrite"]]
        if model_names:
            log_format = f"DEPLOY - {'OVERWRITE':<15} - backward_steps"
            _logger.info(f"{log_format} - {' -> '.join(backward_steps)} for {model_names}")
            graph.remove(config=config, model_names=model_names, space_types=[space_type], backward_steps=backward_steps, log_format=log_format)
        else:
            _logger.info(f"DEVELOP - {'OVERWRITE':<15} - Nothing to overwrite.")
    else:
        _logger.info(f"DEPLOY - {'OVERWRITE':<15} - Nothing to overwrite")


def deploy_create(config: dict, model_configs: list, space_type: str, check_require_steps: list, forward_steps: list) -> None:
    """
    Create deployments that are specified in ``model_configs``.

    Args:
        config (dict): configuration dictionary
        model_configs (list[dict]): models to be removed
        space_type (str): development or production environment
        check_require_steps (list[str]): list of steps to create upstream assets
        forward_steps (list[str]): list of steps to create downstream assets
    """
    all_deployments = wml.get_deployments(config=config, space_type=space_type)
    model_configs = [x for x in model_configs if wml.get_model_deployment_name(model_name=x["model_name"]) not in all_deployments.keys()]
    if model_configs:
        for model_config in model_configs:
            model_name = model_config["model_name"]
            args = {
                "config": config,
                "model_config": model_config,
                "model_name": model_name,
                "space_types": [space_type],
            }
            log_format = f"DEPLOY - {'REQUIREMENTS':<15} - require_steps"
            args["log_format"] = log_format
            _logger.info(f"{log_format} - {' -> '.join(check_require_steps)} for {model_name}.")
            results = graph.run(direction="require", steps=check_require_steps, args=args)

            require_steps = [k for k, v in results.items() if not v]
            forward_steps = require_steps + forward_steps
            log_format = f"DEPLOY - {'CREATE':<15} - forward_steps"
            args["log_format"] = log_format
            _logger.info(f"{log_format} - {' -> '.join(forward_steps)} for {model_name}.")
            graph.run(direction="forward", steps=forward_steps, args=args)
    else:
        _logger.info(f"DEPLOY - {'CREATE':<15} - Nothing to create")


class deploy:
    """
    Handles delete and apply commands.
    """

    @staticmethod
    def delete(config: dict, model_names: list, space_type: str) -> None:
        """
        Removes model deployments specified in ``model_configs``.

        Args:
            config (dict): configuration dictionary
            model_names (list[str]): models to be removed, updated, overwritten or created
        """
        model_names_copy = model_names[:]
        _logger.info(f"DEPLOY - {'START':<15} - {model_names}.")

        backward_steps = graph.get_backward_steps(source="promote_model", target="subscribe_model")
        model_configs = [x for x in config["model_configs"] if x["model_name"] in model_names]

        # remove
        deploy_remove(config=config, model_configs=model_configs, space_type=space_type, backward_steps=backward_steps)

        _logger.info(f"DEPLOY - {'COMPLETED':<15} - {model_names_copy}.")

    @staticmethod
    def apply(config: dict, model_names: list, space_type: str) -> None:
        """
        Create model deployments specified in ``model_configs``.

        Args:
            config (dict): configuration dictionary
            model_names (list[str]): deployments to be removed, updated, overwritten or created
            space_type (str): development or production environment
        """
        model_names_copy = model_names[:]
        _logger.info(f"DEPLOY - {'START':<15} - {model_names}")

        forward_steps = graph.get_forward_steps(source="promote_model", target="deploy_model")
        backward_steps = graph.get_backward_steps(source="promote_model", target="subscribe_model")
        check_require_steps = graph.get_check_require_steps(source="run_model", target="promote_model")

        model_configs = [x for x in config["model_configs"] if x["model_name"] in model_names]

        # update
        deploy_update(config=config, model_configs=model_configs, space_type=space_type)

        # overwrite
        deploy_overwrite(config=config, model_configs=model_configs, space_type=space_type, backward_steps=backward_steps)

        # create
        deploy_create(config=config, model_configs=model_configs, space_type=space_type, check_require_steps=check_require_steps, forward_steps=forward_steps)

        _logger.info(f"DEPLOY - {'COMPLETED':<15} - {model_names_copy}")


# def deploy_remove_declarative(config: dict, model_configs: list[dict], space_type: str, backward_steps: list[str]) -> None:
#     """
#     Remove deployments that are not specified in ``model_configs``.

#     Args:
#         config (dict): configuration dictionary
#         model_configs (list[dict]): models to be removed
#         space_type (str): development or production environment
#         backward_steps (list[str]): list of steps to remove downstream assets
#     """
#     all_models = wml.get_models(config=config, space_type=space_type)
#     model_names = [x["model_name"] for x in model_configs]
#     delete_models = [x for x in all_models.keys() if x not in model_names]
#     if delete_models:
#         log_format = f"DEPLOY - {'REMOVE':<15} - backward_steps"
#         _logger.info(f"{log_format} - {' -> '.join(backward_steps)} for {model_names}")
#         graph.remove(config=config, model_names=delete_models, space_types=[space_type], backward_steps=backward_steps, log_format=log_format)
#     else:
#         _logger.info(f"DEPLOY - {'REMOVE':<15} - Nothing to remove")


# def deploy_declarative(config: dict, model_names: list[str], space_type: str) -> None:
#     """
#     Remove, update, overwrite or create deployments specified in ``model_configs``.

#     Args:
#         config (dict): configuration dictionary
#         model_names (list[str]): deployments to be removed, updated, overwritten or created
#         space_type (str): development or production environment
#     """
#     model_names_copy = model_names[:]
#     _logger.info(f"DEPLOY - {'START':<15} - {model_names}")

#     forward_steps = graph.get_forward_steps(source="promote_model", target="deploy_model")
#     backward_steps = graph.get_backward_steps(source="promote_model", target="subscribe_model")
#     check_require_steps = graph.get_check_require_steps(source="run_model", target="promote_model")

#     model_configs = [x for x in config["model_configs"] if x["model_name"] in model_names]

#     # remove deployments that are not specified
#     deploy_remove_declarative(config=config, model_configs=model_configs, space_type=space_type, backward_steps=backward_steps)

#     # update
#     deploy_update(config=config, model_configs=model_configs, space_type=space_type)

#     # overwrite
#     deploy_overwrite(config=config, model_configs=model_configs, space_type=space_type, backward_steps=backward_steps)

#     # create
#     deploy_create(config=config, model_configs=model_configs, space_type=space_type, check_require_steps=check_require_steps, forward_steps=forward_steps)

#     _logger.info(f"DEPLOY - {'COMPLETED':<15} - {model_names_copy}")
