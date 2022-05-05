"""
Run models.
"""
import logging
import importlib
import pandas as pd

_logger = logging.getLogger(__name__)


def run_model(model_config: dict, log_format: str) -> None:
    """
    Run model and assigns the following to the `model_config` dictionary.

    - model: a fitted model
    - custom metrics: additional metrics to log in Factsheets
    - input data schema: schema of the training data
    - target: column name of target variable

    Args:
        config (dict): configuration dictionary
        log_format (str): log format for this method

    """
    model_name = model_config["model_name"]
    _logger.info(f"{log_format} - running model ... {model_name}.")
    model_module = importlib.import_module(model_config["model_script"].replace(".py", ""))
    if hasattr(model_module, "model"):
        model_config["model"] = model_module.model
    model_config["custom_metrics"] = model_module.custom_metrics
    model_config["input_data_schema"] = model_module.input_data_schema
    model_config["target"] = model_module.y.name
    # model_config["X"] = model_module.X
    # model_config["y"] = model_module.y
    _logger.info(f"{log_format} - run_model completed for {model_name}.")


def get_input_data_schema(X: pd.DataFrame) -> list:
    """
    Get input data schema.

    Args:
        X (pd.DataFrame): Data frame used to train model.
    
    Returns:
        list[dict]: a list of dictionary from training fields.
    """

    return [{"id": "input_data_schema", "type": "list", "fields": [{"name": index, "type": value} for index, value in X.dtypes.astype(str).items()]}]
