"""
Subscribe and evaluate model on OpenScale in development or production.
"""
import logging
import pandas as pd
from cpdflow import graph
from cpdflow.wos import wos
from cpdflow.wml import wml
import functools

_logger = logging.getLogger(__name__)


def subscribe_remove(config: dict, model_configs: list, space_type: str, backward_steps: list) -> None:
    """
    Remove subscriptions that are not specified in ``model_configs``.

    Args:
        config (dict): configuration dictionary
        model_configs (list[dict]): models to be removed
        space_type (str): development or production environment
        backward_steps (list[str]): list of steps to remove downstream assets
    """
    all_subscriptions = wos.get_subscriptions(config)
    model_names = [x["model_name"] for x in model_configs]
    delete_subscriptions_model_names = [
        wos.get_model_name_from_subscription_name(subscription_name=x, space_type=space_type)
        for x in all_subscriptions.keys()
        if wos.get_model_name_from_subscription_name(subscription_name=x, space_type=space_type) in model_names
    ]
    if delete_subscriptions_model_names:
        log_format = f"SUBSCRIBE - {'REMOVE':<15} - backward_steps"
        _logger.info(f"{log_format} - {' -> '.join(backward_steps)} for {delete_subscriptions_model_names}")
        graph.remove(config=config, model_names=delete_subscriptions_model_names, space_types=[space_type], backward_steps=backward_steps, log_format=log_format)
    else:
        _logger.info(f"SUBSCRIBE - {'REMOVE':<15} - Nothing to remove")


def subscribe_overwrite(config: dict, model_configs: list, space_type: str, backward_steps: list) -> None:
    """
    Remove subscriptions that are specified in ``model_configs``.

    Args:
        config (dict): configuration dictionary
        model_configs (list[dict]): subscriptions to be removed
        backward_steps (list[str]): list of steps to remove assets
    """
    if model_configs:
        model_names = [x["model_name"] for x in model_configs if x["overwrite"]]
        if model_names:
            log_format = f"SUBSCRIBE - {'OVERWRITE':<15} - backward_steps"
            _logger.info(f"{log_format} - {' -> '.join(backward_steps)} for {model_names}")
            graph.remove(config=config, model_names=model_names, space_types=[space_type], backward_steps=backward_steps, log_format=log_format)
        else:
            _logger.info(f"SUBSCRIBE - {'OVERWRITE':<15} - Nothing to overwrite.")
    else:
        _logger.info(f"SUBSCRIBE - {'OVERWRITE':<15} - Nothing to overwrite")


def subscribe_create(config: dict, model_configs: list, space_type: str, scoring_payload: dict, feedback_payload: dict) -> None:
    """
    Create subscriptions that are specified in ``model_configs``.

    Args:
        config (dict): configuration dictionary
        model_configs (list[dict]): subscriptions to be created
        space_type (str): development or production environment
        scoring_payload (dict): payload for scoring
        feedback_payload (pd.Dataframe): payload to store feedback
    """
    all_subscriptions = wos.get_subscriptions(config)
    model_configs = [x for x in model_configs if wos.get_subscription_name(model_name=x["model_name"], space_type=space_type) not in all_subscriptions.keys()]
    if model_configs:
        for model_config in model_configs:
            include = ["store_payload"] if "scoring_url" in model_config else ["score_model"]
            check_require_steps_source = "get_metadata" if "scoring_url" in model_config else "run_model"

            forward_steps = graph.get_forward_steps(source="subscribe_model", target="evaluate", include=include)
            check_require_steps = graph.get_check_require_steps(source=check_require_steps_source, target="subscribe_model")
            model_name = model_config["model_name"]
            args = {
                "config": config,
                "model_config": model_config,
                "model_name": model_name,
                "scoring_payload": scoring_payload,
                "feedback_payload": feedback_payload,
                "custom_monitor_config": None,
                "space_types": [space_type],
            }

            log_format = f"SUBSCRIBE - {'REQUIREMENTS':<15} - require_steps"
            args["log_format"] = log_format
            _logger.info(f"{log_format} - {' -> '.join(check_require_steps)} for {model_name}.")
            results = graph.run(direction="require", steps=check_require_steps, args=args)
            require_steps = [k for k, v in results.items() if not v]

            forward_steps = require_steps + forward_steps
            log_format = f"SUBSCRIBE - {'CREATE':<15} - forward_steps"
            args["log_format"] = log_format
            _logger.info(f"{log_format} - {' -> '.join(forward_steps)} for {model_name}.")
            graph.run(direction="forward", steps=forward_steps, args=args)
    else:
        _logger.info(f"SUBSCRIBE - {'CREATE':<15} - Nothing to create")


def custom_metric_overwrite(config: dict, space_type: str) -> None:
    """
    Remove subscriptions that are specified in ``model_configs``.

    Args:
        config (dict): configuration dictionary
    """
    log_format = f"SUBSCRIBE - {'OVERWRITE':<15} - remove custom metric"
    _logger.info(f"{log_format} - {config['custom_metric']['custom_monitor_name']}.")

    custom_monitor_name = config["custom_metric"]["custom_monitor_name"]
    custom_metric_function_name = wos.get_custom_monitor_function_name(custom_monitor_name=custom_monitor_name)
    function_deployment_name = wml.get_function_deployment_name(function_name=custom_metric_function_name)
    wos.delete_custom_metric_monitor_by_custom_monitor_name(config=config, log_format=log_format)
    wos.delete_integrated_system_by_custom_monitor_name(config=config, log_format=log_format)
    wml.delete_function_deployment_by_function_deployment_names(config=config, function_deployment_names=[function_deployment_name], space_type=space_type)
    wml.delete_function_by_function_names(config=config, function_names=[custom_metric_function_name], space_type=space_type, log_format=log_format)


def subscribe(config: dict, model_names: list, space_type: str) -> None:
    """
    Remove, overwrite or create subscriptions that are specified in ``model_configs``.

    Handles the ``validate`` and ``operate`` lifecycle stages.

    Args:
        config (dict): configuration dictionary
        model_names (list[str]): subscriptions to be removed, updated, overwritten or created
    """
    model_names_copy = model_names[:]
    _logger.info(f"SUBSCRIBE - {'START':<15} - {model_names}")

    backward_steps = graph.get_backward_steps(source="subscribe_model", target="evaluate")

    df_scoring_payload = pd.read_csv(config["scoring_payload"]["file_name"])
    df_meta_payload = pd.read_csv(config["meta_payload"]["file_name"])
    meta_payload = {"fields": df_meta_payload.columns.tolist(), "values": df_meta_payload.values.tolist()}
    scoring_payload = {"input_data": [{"fields": df_scoring_payload.columns.tolist(), "values": df_scoring_payload.values.tolist(), "meta": meta_payload}]}
    feedback_payload = pd.read_csv(config["feedback_payload"]["file_name"])

    model_configs = [x for x in config["model_configs"] if x["model_name"] in model_names]
    model_names = [x["model_name"] for x in model_configs]

    # remove
    subscribe_remove(config=config, model_configs=model_configs, space_type=space_type, backward_steps=backward_steps)

    # overwrite
    subscribe_overwrite(config=config, model_configs=model_configs, space_type=space_type, backward_steps=backward_steps)

    # custom metric
    if "custom_metric" in config:
        if "overwrite" in config["custom_metric"]:
            custom_metric_overwrite(config=config, space_type=space_type)
        wos.create_custom_metric_provider(config=config, space_type=space_type)
        wos.create_integrated_system(config=config, space_type=space_type)
        wos.create_custom_metric_monitor(config=config)

    # create
    subscribe_create(config=config, model_configs=model_configs, space_type=space_type, scoring_payload=scoring_payload, feedback_payload=feedback_payload)

    # evaluate
    evaluate(config=config, model_names=model_names, space_type=space_type)

    _logger.info(f"SUBSCRIBE - {'COMPLETED':<15} - {model_names_copy}")


def evaluate(config: dict, model_names: list, space_type: str) -> None:
    """
    Evaluates the models.

    Args:
        config (dict): configuration dictionary
        model_names (list[str]): subscriptions to be removed, updated, overwritten or created
    """
    log_format = f"EVALUATE"
    for model_name in model_names:
        wos.evaluate(config=config, model_name=model_name, space_type=space_type, log_format=log_format)


class validate:
    """
    Handles delete and apply commands.
    """

    @staticmethod
    def delete(config: dict, model_names: list) -> None:
        """
        Remove subscriptions specified in ``model_configs``.

        Handles the ``validate`` and ``operate`` lifecycle stages.

        Args:
            config (dict): configuration dictionary
            model_names (list[str]): subscriptions to be removed, updated, overwritten or created
        """
        model_names_copy = model_names[:]
        _logger.info(f"SUBSCRIBE - {'START':<15} - {model_names}")

        backward_steps = graph.get_backward_steps(source="subscribe_model", target="evaluate")
        model_configs = [x for x in config["model_configs"] if x["model_name"] in model_names]
        model_names = [x["model_name"] for x in model_configs]

        # remove
        subscribe_remove(config=config, model_configs=model_configs, space_type="dev", backward_steps=backward_steps)

        _logger.info(f"SUBSCRIBE - {'COMPLETED':<15} - {model_names_copy}")

    @staticmethod
    def apply(config: dict, model_names: list) -> None:
        """
        Remove, overwrite or create subscriptions that are specified in ``model_configs``.

        Handles the ``validate`` and ``operate`` lifecycle stages.

        Args:
            config (dict): configuration dictionary
            model_names (list[str]): subscriptions to be removed, updated, overwritten or created
        """
        subscribe(config=config, model_names=model_names, space_type="dev")


class operate:
    """
    Handles delete and apply commands.
    """

    @staticmethod
    def delete(config: dict, model_names: list) -> None:
        """
        Remove subscriptions specified in ``model_configs``.

        Handles the ``validate`` and ``operate`` lifecycle stages.

        Args:
            config (dict): configuration dictionary
            model_names (list[str]): subscriptions to be removed, updated, overwritten or created
        """
        model_names_copy = model_names[:]
        _logger.info(f"SUBSCRIBE - {'START':<15} - {model_names}")

        backward_steps = graph.get_backward_steps(source="subscribe_model", target="evaluate")
        model_configs = [x for x in config["model_configs"] if x["model_name"] in model_names]
        model_names = [x["model_name"] for x in model_configs]

        # remove
        subscribe_remove(config=config, model_configs=model_configs, space_type="prod", backward_steps=backward_steps)

        _logger.info(f"SUBSCRIBE - {'COMPLETED':<15} - {model_names_copy}")

    @staticmethod
    def apply(config: dict, model_names: list) -> None:
        """
        Remove, overwrite or create subscriptions that are specified in ``model_configs``.

        Handles the ``validate`` and ``operate`` lifecycle stages.

        Args:
            config (dict): configuration dictionary
            model_names (list[str]): subscriptions to be removed, updated, overwritten or created
        """
        subscribe(config=config, model_names=model_names, space_type="prod")


# validate = functools.partial(subscribe, space_type="dev")

# operate = functools.partial(subscribe, space_type="prod")


# def subscribe_remove_declarative(config: dict, model_configs: list[dict], space_type: str, backward_steps: list[str]) -> None:
#     """
#     Remove subscriptions that are not specified in ``model_configs``.

#     Args:
#         config (dict): configuration dictionary
#         model_configs (list[dict]): models to be removed
#         space_type (str): development or production environment
#         backward_steps (list[str]): list of steps to remove downstream assets
#     """
#     all_subscriptions = wos.get_subscriptions(config)
#     model_names = [x["model_name"] for x in model_configs]
#     delete_subscriptions_model_names = [
#         wos.get_model_name_from_subscription_name(subscription_name=x, space_type=space_type)
#         for x in all_subscriptions.keys()
#         if wos.get_model_name_from_subscription_name(subscription_name=x, space_type=space_type) not in model_names
#     ]
#     if delete_subscriptions_model_names:
#         log_format = f"SUBSCRIBE - {'REMOVE':<15} - backward_steps"
#         _logger.info(f"{log_format} - {' -> '.join(backward_steps)} for {delete_subscriptions_model_names}")
#         graph.remove(config=config, model_names=delete_subscriptions_model_names, space_types=[space_type], backward_steps=backward_steps, log_format=log_format)
#     else:
#         _logger.info(f"SUBSCRIBE - {'REMOVE':<15} - Nothing to remove")


# def subscribe_declarative(config: dict, model_names: list[str], space_type: str) -> None:
#     """
#     Remove, overwrite or create subscriptions that are specified in ``model_configs``.

#     Handles the ``validate`` and ``operate`` lifecycle stages.

#     Args:
#         config (dict): configuration dictionary
#         model_names (list[str]): subscriptions to be removed, updated, overwritten or created
#     """
#     model_names_copy = model_names[:]
#     _logger.info(f"SUBSCRIBE - {'START':<15} - {model_names}")

#     backward_steps = graph.get_backward_steps(source="subscribe_model", target="evaluate")

#     df_scoring_payload = pd.read_csv(config["scoring_payload"]["file_name"])
#     df_meta_payload = pd.read_csv(config["meta_payload"]["file_name"])
#     meta_payload = {"fields": df_meta_payload.columns.tolist(), "values": df_meta_payload.values.tolist()}
#     scoring_payload = {"input_data": [{"fields": df_scoring_payload.columns.tolist(), "values": df_scoring_payload.values.tolist(), "meta": meta_payload}]}
#     feedback_payload = pd.read_csv(config["feedback_payload"]["file_name"])

#     model_configs = [x for x in config["model_configs"] if x["model_name"] in model_names]
#     model_names = [x["model_name"] for x in model_configs]

#     # remove
#     subscribe_remove_declarative(config=config, model_configs=model_configs, space_type=space_type, backward_steps=backward_steps)

#     # overwrite
#     subscribe_overwrite(config=config, model_configs=model_configs, space_type=space_type, backward_steps=backward_steps)

#     # custom metric
#     if "custom_metric" in config:
#         if "overwrite" in config["custom_metric"]:
#             custom_metric_overwrite(config=config, space_type=space_type)
#         wos.create_custom_metric_provider(config=config, space_type=space_type)
#         wos.create_integrated_system(config=config, space_type=space_type)
#         wos.create_custom_metric_monitor(config=config)

#     # create
#     subscribe_create(config=config, model_configs=model_configs, space_type=space_type, scoring_payload=scoring_payload, feedback_payload=feedback_payload)

#     # evaluate
#     evaluate(config=config, model_names=model_names, space_type=space_type)

#     _logger.info(f"SUBSCRIBE - {'COMPLETED':<15} - {model_names_copy}")


# root_nodes = [n for n, d in graph.G.in_degree() if d == 0]
# requirements = {x: nx.shortest_path(G=graph.G, source=x, target="subscribe_model")[:-1] for x in root_nodes}
# requirement_steps = []
# check_require_steps = requirements["run_model"]
# log_format = f"SUBSCRIBE - {'REQUIREMENTS':<15} - require_steps"
# args["log_format"] = log_format
# _logger.info(f"{log_format} - {' -> '.join(check_require_steps)} for {model_name}.")
# results = graph.run(direction="require", steps=check_require_steps, args=args)
# require_steps = [k for k, v in results.items() if not v]
# requirement_steps.append(require_steps)
# if "custom_metric" in config:
#     requirement_steps.append(requirements["create_custom_metric_provider"])
# Parallel(n_jobs=2, prefer="threads")(delayed(graph.run)(direction="forward", steps=x, args=args) for x in requirement_steps)
