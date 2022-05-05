"""
Runs and stores model in project space with Factsheets.
"""
import logging
from cpdflow import graph
from cpdflow.wml import wml
from cpdflow.ws import ws

_logger = logging.getLogger(__name__)


def develop_remove(config: dict, model_configs: list, space_types: list, backward_steps: list) -> None:
    """
    Remove models that are specified in ``model_configs``.

    Args:
        config (dict): configuration dictionary
        model_configs (list[dict]): models to be removed
        space_types (list[str]): development or production environment
        backward_steps (list[str]): list of steps to remove downstream assets
    """
    all_models = wml.get_models(config=config, space_type="project")
    model_names = [x["model_name"] for x in model_configs]
    delete_models = [x for x in all_models.keys() if x in model_names]
    if delete_models:
        log_format = f"DEVELOP - {'REMOVE':<15} - backward_steps"
        _logger.info(f"{log_format} - {' -> '.join(backward_steps)} for {delete_models}.")
        graph.remove(config=config, model_names=delete_models, space_types=space_types, backward_steps=backward_steps, log_format=log_format)
    else:
        _logger.info(f"DEVELOP - {'REMOVE':<15} - Nothing to remove.")


def develop_update(config: dict, model_configs: list, update_steps: list) -> None:
    """
    Update models that are specified in ``model_configs``.

    Args:
        config (dict): configuration dictionary
        model_configs (list[dict]): models to be removed
        update_steps (list[str]): list of steps to update assets
    """
    all_models = wml.get_models(config=config, space_type="project")
    model_configs = [x for x in model_configs if x["update"] and x["model_name"] in all_models]
    if model_configs:
        for model_config in model_configs:
            model_name = model_config["model_name"]
            log_format = f"DEVELOP - {'UPDATE':<15} - update_steps"
            _logger.info(f"{log_format} - {' -> '.join(update_steps)} for {model_name}.")
            args = {"config": config, "model_config": model_config, "space_types": ["project"], "log_format": log_format}
            graph.run(direction="forward", steps=update_steps, args=args)
            ws.update_model(config=config, model_config=model_config, log_format=log_format)
    else:
        _logger.info(f"DEVELOP - {'UPDATE':<15} - Nothing to update.")


def develop_overwrite(config: dict, model_configs: list, space_types: list, backward_steps: list) -> None:
    """
    Overwrite models that are specified in ``model_configs``.

    Args:
        config (dict): configuration dictionary
        model_configs (list[dict]): models to be removed
        space_types (list[str]): development or production environment
        backward_steps (list[str]): list of steps to remove downstream assets
    """
    all_models = wml.get_models(config=config, space_type="project")
    if model_configs:
        model_names = [x["model_name"] for x in model_configs if x["overwrite"] and x["model_name"] in all_models]
        if model_names:
            log_format = f"DEVELOP - {'OVERWRITE':<15} - backward_steps"
            _logger.info(f"{log_format} - {' -> '.join(backward_steps)} for {model_names}.")
            graph.remove(config=config, model_names=model_names, space_types=space_types, backward_steps=backward_steps, log_format=log_format)
        else:
            _logger.info(f"DEVELOP - {'OVERWRITE':<15} - Nothing to overwrite.")
    else:
        _logger.info(f"DEVELOP - {'OVERWRITE':<15} - Nothing to overwrite.")


def develop_create(config: dict, model_configs: list, forward_steps: list) -> None:
    """
    Create models that are specified in ``model_configs``.

    Args:
        config (dict): configuration dictionary
        model_configs (list[dict]): models to be removed
        forward_steps (list[str]): list of steps to create downstream assets
    """
    all_models = wml.get_models(config=config, space_type="project")
    model_configs = [x for x in model_configs if x["model_name"] not in all_models.keys()]
    if model_configs:
        for model_config in model_configs:
            model_name = model_config["model_name"]
            log_format = f"DEVELOP - {'CREATE':<15} - forward_steps"
            _logger.info(f"{log_format} - {' -> '.join(forward_steps)} for {model_name}.")
            args = {"config": config, "model_config": model_config, "space_types": ["project"], "log_format": log_format}
            graph.run(direction="forward", steps=forward_steps, args=args)
    else:
        _logger.info(f"DEVELOP - {'CREATE':<15} - Nothing to create.")


class develop:
    """
    Handles delete and apply commands.
    """

    @staticmethod
    def delete(config: dict, model_names: list) -> None:
        """
        Removes models specified in ``model_configs``.

        Args:
            config (dict): configuration dictionary
            model_names (list[str]): models to be removed, updated, overwritten or created
        """
        model_names_copy = model_names[:]
        _logger.info(f"DEVELOP - {'START':<15} - {model_names}.")

        backward_steps = graph.get_backward_steps(source="run_model", target="subscribe_model")
        model_configs = [x for x in config["model_configs"] if x["model_name"] in model_names]

        # remove
        develop_remove(config=config, model_configs=model_configs, space_types=["dev", "prod"], backward_steps=backward_steps)

        _logger.info(f"DEVELOP - {'COMPLETED':<15} - {model_names_copy}.")

    @staticmethod
    def apply(config: dict, model_names: list) -> None:
        """
        Update, overwrite or create models specified in ``model_configs``.

        Args:
            config (dict): configuration dictionary
            model_names (list[str]): models to be removed, updated, overwritten or created
        """
        model_names_copy = model_names[:]
        _logger.info(f"DEVELOP - {'START':<15} - {model_names}.")

        forward_steps = graph.get_forward_steps(source="run_model", target="register_model")
        backward_steps = graph.get_backward_steps(source="run_model", target="subscribe_model")
        update_steps = graph.get_forward_steps(source="run_model", target="export_facts")

        model_configs = [x for x in config["model_configs"] if x["model_name"] in model_names]

        # update
        develop_update(config=config, model_configs=model_configs, update_steps=update_steps)

        # overwrite
        develop_overwrite(config=config, model_configs=model_configs, space_types=["dev", "prod"], backward_steps=backward_steps)

        # create
        develop_create(config=config, model_configs=model_configs, forward_steps=forward_steps)

        _logger.info(f"DEVELOP - {'COMPLETED':<15} - {model_names_copy}.")


# def develop_remove_declarative(config: dict, model_configs: list[dict], space_types: list[str], backward_steps: list[str]) -> None:
#     """
#     Remove models that are not specified in ``model_configs``.

#     Args:
#         config (dict): configuration dictionary
#         model_configs (list[dict]): models to be removed
#         space_types (list[str]): development or production environment
#         backward_steps (list[str]): list of steps to remove downstream assets
#     """
#     all_models = wml.get_models(config=config, space_type="project")
#     model_names = [x["model_name"] for x in model_configs]
#     delete_models = [x for x in all_models.keys() if x not in model_names]
#     if delete_models:
#         log_format = f"DEVELOP - {'REMOVE':<15} - backward_steps"
#         _logger.info(f"{log_format} - {' -> '.join(backward_steps)} for {delete_models}.")
#         graph.remove(config=config, model_names=delete_models, space_types=space_types, backward_steps=backward_steps, log_format=log_format)
#     else:
#         _logger.info(f"DEVELOP - {'REMOVE':<15} - Nothing to remove.")


# def develop_declarative(config: dict, model_names: list) -> None:
#     """
#     Remove, update, overwrite or create models that are specified in ``model_configs``.

#     Args:
#         config (dict): configuration dictionary
#         model_names (list[str]): models to be removed, updated, overwritten or created
#     """
#     model_names_copy = model_names[:]
#     _logger.info(f"DEVELOP - {'START':<15} - {model_names}.")

#     forward_steps = graph.get_forward_steps(source="run_model", target="register_model")
#     backward_steps = graph.get_backward_steps(source="run_model", target="subscribe_model")
#     update_steps = graph.get_forward_steps(source="run_model", target="export_facts")

#     model_configs = [x for x in config["model_configs"] if x["model_name"] in model_names]

#     # remove
#     develop_remove_declarative(config=config, model_configs=model_configs, space_types=["dev", "prod"], backward_steps=backward_steps)

#     # update
#     develop_update(config=config, model_configs=model_configs, update_steps=update_steps)

#     # overwrite
#     develop_overwrite(config=config, model_configs=model_configs, space_types=["dev", "prod"], backward_steps=backward_steps)

#     # create
#     develop_create(config=config, model_configs=model_configs, forward_steps=forward_steps)

#     _logger.info(f"DEVELOP - {'COMPLETED':<15} - {model_names_copy}.")
