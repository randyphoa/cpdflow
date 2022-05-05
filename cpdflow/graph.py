"""
Graph operations.
"""
import logging

import networkx as nx

from cpdflow.wkc import wkc
from cpdflow.wml import wml
from cpdflow.wos import wos
from cpdflow.ws import ws
from cpdflow.model import model

_logger = logging.getLogger(__name__)


return_false = lambda : False


graph_operation = {
    "run_model": {
        "forward": [model.run_model], 
        "backward": None, 
        "require": [wml.check_model_stored]
    },
    "get_metadata": {
        "forward": [model.run_model], 
        "backward": None, 
        "require": [return_false]
    },
    "export_facts": {
        "forward": [wkc.export_facts], 
        "backward": None, 
        "require": [wml.check_model_stored]
    },
    "store_model": {
        "forward": [ws.store_model], 
        "backward": [ws.delete_model_from_project_by_model_names], 
        "require": [wml.check_model_stored]
    },
    "register_model": {
        "forward": [wkc.register_model_from_project], 
        "backward": [wkc.delete_model_from_project_inventory_by_model_names], 
        "require": [wml.check_model_stored]
    },
    "promote_model": {
        "forward": [wml.promote_model], 
        "backward": [wkc.delete_model_from_inventory_by_model_names, wml.delete_model_by_model_names], 
        "require": [wml.check_model_promoted]
    },
    "deploy_model": {
        "forward": [wml.deploy_model], 
        "backward": [wml.delete_model_deployment_by_model_deployment_names], 
        "require": [wml.check_model_deployed]
    },
    "create_metric_provider": {
        "forward": [wos.create_custom_metric_provider], 
        "backward": None, 
        "require": None
    },
    "create_integrated_system": {
        "forward": [wos.create_integrated_system], 
        "backward": None, 
        "require": None
    },
    "create_metric_monitor": {
        "forward": [wos.create_custom_metric_monitor], 
        "backward": None, 
        "require": None
    },
    "verify_ml_provider": {
        "forward": None, 
        "backward": None, 
        "require": [return_false]
    },
    "subscribe_model": {
        "forward": [wos.subscribe_model], 
        "backward": [wos.delete_subscription_by_subscription_names], 
        "require": None
    },
    "store_payload": {
        "forward": [wos.store_payload], 
        "backward": None, 
        "require": None
    },
    "score_model": {
        "forward": [wml.score_model], 
        "backward": None, 
        "require": None
    },
    "create_monitor": {
        "forward": [wos.create_monitor], 
        "backward": None, 
        "require": None
    },
    "store_feedback": {
        "forward": [wos.store_feedback], 
        "backward": None, 
        "require": None
    },
    "evaluate": {
        "forward": [wos.evaluate], 
        "backward": None, 
        "require": None
    },
}


dependency_graph = [
    ("run_model", "export_facts"),
    ("export_facts", "store_model"),
    ("store_model", "register_model"),
    ("register_model", "promote_model"),
    # ("run_auto_ai", "promote_model"),
    ("promote_model", "deploy_model"),
    ("deploy_model", "subscribe_model"),
    ("create_metric_provider", "create_integrated_system"),
    ("create_integrated_system", "create_metric_monitor"),
    ("create_metric_monitor", "subscribe_model"),
    ("get_metadata", "verify_ml_provider"),
    ("verify_ml_provider", "subscribe_model"),
    # ("load_data", "subscribe_model"),
    ("subscribe_model", "score_model"),
    ("score_model", "create_monitor"),
    ("subscribe_model", "store_payload"),
    ("store_payload", "create_monitor"),
    ("create_monitor", "store_feedback"),
    ("store_feedback", "evaluate"),
]

G = nx.DiGraph()
G.add_edges_from(dependency_graph)
for x in G.nodes:
    for k, v in graph_operation[x].items():
        G.nodes[x][k] = v

def get_execution_plan(source: str, target: str, include: list = None) -> list:
    """
    Get execution plan.

    Args:
        source (str): source
        target (str): target
        include (list[str]): steps to include

    Returns:
        list[str]: execution steps
    """
    plans = list(nx.all_simple_paths(G=G, source=source, target=target))
    if include:
        include = set(include)
        for plan in plans:
            if not include - set(plan):
                return plan
    return plans[0]


def get_forward_steps(source: str, target: str, include: list = None) -> list:
    """
    Get forward steps.

    Args:
        source (str): source
        target (str): target
        include (list[str]): steps to include

    Returns:
        list[str]: forward steps
    """
    return get_execution_plan(source=source, target=target, include=include)


def get_backward_steps(source: str, target: str, include: list = None) -> list:
    """
    Get backward steps.

    Args:
        source (str): source
        target (str): target
        include (list[str]): steps to include

    Returns:
        list[str]: backward steps
    """
    return list(reversed(get_execution_plan(source=source, target=target, include=include)))


def get_check_require_steps(source: str, target: str, include: list = None) -> list:
    """
    Get requirement steps.

    Args:
        source (str): source
        target (str): target
        include (list[str]): steps to include

    Returns:
        list[str]: requirement steps
    """
    return get_execution_plan(source=source, target=target, include=include)[:-1]


def run(direction: str, steps: list, args: dict) -> None:
    """
    Run steps.

    Args:
        direction (str): forward, backward or require
        steps (list[str]): steps to be run
        args (dict): other arguments
    """
    results = {}
    log_format = args["log_format"]
    space_types = args["space_types"]
    for step in steps:
        if G.nodes[step][direction]:
            for x in G.nodes[step][direction]:
                for space_type in space_types:
                    _logger.info(f"{log_format} - running ... {x.__name__} in {space_type}.")
                    args["space_type"] = space_type
                    f_code = x.__code__
                    required_args = f_code.co_varnames[: f_code.co_argcount + f_code.co_kwonlyargcount]
                    results[step] = x(**{k: v for k, v in args.items() if k in required_args})
    return results


def remove(config: dict, model_names: list, space_types: list, backward_steps: list, log_format: str):
    """
    Remove steps.

    Args:
        config (dict): configuration dictionary
        model_names (list[str]): model names
        space_types (list[str]): development or production
        backward_steps (list[str]): backward steps to run
        log_format (str): log format for this method
    """
    model_deployment_names = [wml.get_model_deployment_name(x) for x in model_names]
    subscription_names = []
    for space_type in space_types:
        for x in model_names:
            subscription_names.append(wos.get_subscription_name(x, space_type=space_type))
    args = {
        "config": config,
        "subscription_names": subscription_names,
        "model_deployment_names": model_deployment_names,
        "model_names": model_names,
        "space_types": space_types,
        "log_format": log_format,
    }
    run(direction="backward", steps=backward_steps, args=args)


# def export_graph() -> dict:
#     nodes = [{"id": x, "label": x} for x in G.nodes]
#     edges = [{"source": source, "target": target} for source, target in G.edges]
#     data = {
#         "nodes": nodes,
#         "edges": edges,
#     }
#     return data


# def get_execution_plan_pruned(source: str, target: str, include: list[str]) -> list[str]:
#     include = set(include)
#     plans = {len(x): x for x in nx.all_simple_paths(G=G, source=source, target=target)}
#     plans = dict(sorted(plans.items()))
#     idx = 0
#     for i, plan in enumerate(plans.values()):
#         if not include - set(plan):
#             idx = i
#             break
#     steps = list(plans.values())[idx]
#     return steps

# def get_execution_plan(source: str, target: str) -> list[str]:
#     return nx.shortest_path(G=G, source=source, target=target)
