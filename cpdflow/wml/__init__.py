"""
Watson Machine Learning APIs.
"""

from .wml import (
    get_spaces,
    get_model_deployment_name,
    get_function_deployment_name,
    get_models,
    get_model_details,
    get_functions,
    get_deployment_details,
    get_deployments,
    check_model_stored,
    check_model_promoted,
    check_model_deployed,
    delete_model_by_model_names,
    delete_model_deployment_by_model_deployment_names,
    delete_function_by_function_names,
    delete_function_deployment_by_function_deployment_names,
    promote_model,
    deploy_model,
    update_deployed_model,
    deploy_function,
    score_model,
)

