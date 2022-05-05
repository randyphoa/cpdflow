"""
Watson OpenScale APIs.
"""

import json
import requests
import logging
import pandas as pd
import ibm_watson_openscale
from cpdflow.wml import wml
import uuid

IAM_URL = "https://iam.cloud.ibm.com/identity/token"

_logger = logging.getLogger(__name__)


def get_subscription_name(model_name: str, space_type: str) -> str:
    """
    Get subscription name

    Args:
        model_name (str): model name
        space_type (str): development or production environment
    
    Returns:
        str: subscription name
    """
    return model_name + " " + space_type.upper()


def get_custom_monitor_function_name(custom_monitor_name: str) -> str:
    """
    Get custom monitor function name

    Args:
        custom_monitor_name (str): custom monitor name
    
    Returns:
        str: custom monitor function name
    """
    return custom_monitor_name + " Function"


def get_custom_metric_provider_name(custom_monitor_name: str) -> str:
    """
    Get custom monitor provider name

    Args:
        custom_monitor_name (str): custom monitor name
    
    Returns:
        str: custom monitor provider name
    """
    return custom_monitor_name + " Provider"


def get_custom_metric_name(custom_monitor_name: str) -> str:
    """
    Get custom metric name

    Args:
        custom_monitor_name (str): custom monitor name
    
    Returns:
        str: custom metric name
    """
    return custom_monitor_name.replace(" ", "_").lower()


def get_model_name_from_subscription_name(subscription_name: str, space_type: str) -> str:
    """
    Get model name from subscription name

    Args:
        subscription_name (str): subscription name
        space_type (str): development or production environment
    
    Returns:
        str: model name
    """
    return subscription_name.replace(" " + space_type.upper(), "")


def get_subscriptions(config: dict) -> dict:
    """
    Get all subscriptions.

    Args:
        config (dict): configuration dictionary
    
    Returns:
        dict: a dictionary of subscription names as keys and ids as values
    """
    wos_client = config["wos_client"]
    subscriptions = {x["entity"]["deployment"]["name"]: x["metadata"]["id"] for x in wos_client.subscriptions.list().result.to_dict()["subscriptions"]}
    return subscriptions


def get_service_providers(config: dict) -> dict:
    """
    Get all service providers.

    Args:
        config (dict): configuration dictionary
    
    Returns:
        dict: a dictionary of service provider names as keys and ids as values
    """
    wos_client = config["wos_client"]
    service_providers = {x["entity"]["name"]: x["metadata"]["id"] for x in wos_client.service_providers.list().result.to_dict()["service_providers"]}
    return service_providers


def get_integrated_systems(config: dict) -> dict:
    """
    Get all integrated systems.

    Args:
        config (dict): configuration dictionary
    
    Returns:
        dict: a dictionary of integrated_system names as keys and ids as values
    """
    wos_client = config["wos_client"]
    integrated_systems = {
        x["entity"]["name"]: x["metadata"]["id"]
        for x in ibm_watson_openscale.base_classes.watson_open_scale_v2.IntegratedSystems(wos_client).list().result.to_dict()["integrated_systems"]
        if x["entity"]["type"] == "custom_metrics_provider"
    }
    return integrated_systems


def get_monitor_definitions(config: dict) -> dict:
    """
    Get all monitor definitions.

    Args:
        config (dict): configuration dictionary
    
    Returns:
        dict: a dictionary of monitor definition names as keys and ids as values
    """
    wos_client = config["wos_client"]
    monitor_definitions = {x["entity"]["name"]: x["metadata"]["id"] for x in wos_client.monitor_definitions.list().result.to_dict()["monitor_definitions"]}
    return monitor_definitions


def get_monitor_instances_by_subscription_name(config: dict, model_name: str, space_type: str) -> dict:
    """
    Get all monitor instances by subscription name.

    Args:
        config (dict): configuration dictionary
        model_name (str): model name
        space_type (dict): development or production environment
    
    Returns:
        dict: a dictionary of monitor instances names as keys and ids as values
    """
    wos_client = config["wos_client"]
    subscription_name = get_subscription_name(model_name=model_name, space_type=space_type)
    subscriptions = get_subscriptions(config=config)
    subscription_id = subscriptions[subscription_name]
    dict_monitor_instances = {
        x["entity"]["monitor_definition_id"]: x["metadata"]["id"]
        for x in wos_client.monitor_instances.list().result.to_dict()["monitor_instances"]
        if x["entity"]["target"]["target_id"] == subscription_id
    }
    return dict_monitor_instances


def delete_subscription_by_subscription_names(config: dict, subscription_names: list, log_format: str) -> None:
    """
    Delete subscriptions by subscription names.

    Args:
        config (dict): configuration dictionary
        subscription_names (list[str]): subscription names
        log_format (str): log format for this method
    """
    wos_client = config["wos_client"]
    subscriptions = get_subscriptions(config=config)
    for x in subscription_names:
        if x in subscriptions:
            _logger.info(f"{log_format} - deleting ... {x}.")
            wos_client.subscriptions.delete(subscriptions[x], background_mode=False)
            _logger.info(f"{log_format} - deleted {x}.")
    _logger.info(f"{log_format} - delete_subscription_by_subscription_names completed.")


def create_custom_metric_provider(config: dict, space_type: str) -> None:
    """
    Create custom metric provider.

    Args:
        config (dict): configuration dictionary
        space_type (dict): development or production environment
    """
    with open(config["custom_metric"]["custom_metric_script"]) as f:
        calculate_metrics = f.read()

    params = {"apikey": config["apikey"], "calculate_metrics": calculate_metrics}

    def custom_metrics_provider(params=params):
        WOS_URL = "https://api.aiopenscale.cloud.ibm.com"

        import datetime
        import requests
        import pandas as pd

        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        import subprocess

        packages = ["aif360[all]", "category_encoders"]
        subprocess.run(["pip", "install"] + packages + ["--user", "--no-cache-dir"], stderr=subprocess.PIPE, stdout=subprocess.PIPE)

        with open("custom_metric.py", "w") as f:
            f.write(params["calculate_metrics"])

        def get_access_token():
            headers = {"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"}
            data = {"grant_type": "urn:ibm:params:oauth:grant-type:apikey", "apikey": params["apikey"]}
            access_token = requests.post("https://iam.cloud.ibm.com/identity/token", data=data, headers=headers).json()["access_token"]
            return access_token

        def get_feedback_dataset_id(access_token, data_mart_id, subscription_id):
            headers["Authorization"] = "Bearer " + access_token
            DATASETS_URL = f"{WOS_URL}/openscale/{data_mart_id}/v2/data_sets?target.target_id={subscription_id}&target.target_type=subscription&type=feedback"
            json_data = requests.get(DATASETS_URL, headers=headers).json()
            feedback_dataset_id = None
            if "data_sets" in json_data and len(json_data["data_sets"]) > 0:
                feedback_dataset_id = json_data["data_sets"][0]["metadata"]["id"]
            return feedback_dataset_id

        def get_feedback_data(access_token, data_mart_id, feedback_dataset_id):
            json_data = None
            num_records = 100
            if feedback_dataset_id is not None:
                headers["Authorization"] = "Bearer " + access_token
                DATASETS_STORE_RECORDS_URL = f"{WOS_URL}/openscale/{data_mart_id}/v2/data_sets/{feedback_dataset_id}/records?limit={num_records}&format=list"
                json_data = requests.get(DATASETS_STORE_RECORDS_URL, headers=headers, verify=False).json()
                return json_data

        def update_monitor_instance(base_url, access_token, custom_monitor_instance_id, payload):
            monitor_instance_url = f"{base_url}/v2/monitor_instances/{custom_monitor_instance_id}?update_metadata_only=true"
            patch_payload = [{"op": "replace", "path": "/parameters", "value": payload}]
            headers["Authorization"] = "Bearer " + access_token
            response = requests.patch(monitor_instance_url, headers=headers, json=patch_payload, verify=False)
            monitor_response = response.json()
            return response.status_code, monitor_response

        def get_metrics(access_token, data_mart_id, subscription_id):
            import custom_metric

            feedback_dataset_id = get_feedback_dataset_id(access_token, data_mart_id, subscription_id)
            json_data = get_feedback_data(access_token, data_mart_id, feedback_dataset_id)

            fields = json_data["records"][0]["fields"]
            values = json_data["records"][0]["values"]

            df = pd.DataFrame(values, columns=fields)

            metrics = custom_metric.calculate_metrics(df=df)

            return metrics

        def publish_metrics(base_url, access_token, data_mart_id, subscription_id, custom_monitor_id, custom_monitor_instance_id, custom_monitoring_run_id, timestamp):
            custom_metrics = get_metrics(access_token, data_mart_id, subscription_id)
            measurements_payload = [{"timestamp": timestamp, "run_id": custom_monitoring_run_id, "metrics": [custom_metrics]}]
            headers["Authorization"] = "Bearer {}".format(access_token)
            measurements_url = f"{base_url}/v2/monitor_instances/{custom_monitor_instance_id}/measurements"
            response = requests.post(measurements_url, headers=headers, json=measurements_payload)
            published_measurement = response.json()
            return response.status_code, published_measurement

        def publish(input_data):
            timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            payload = input_data["input_data"][0]["values"]
            data_mart_id = payload["data_mart_id"]
            subscription_id = payload["subscription_id"]
            custom_monitor_id = payload["custom_monitor_id"]
            custom_monitor_instance_id = payload["custom_monitor_instance_id"]
            custom_monitor_instance_params = payload["custom_monitor_instance_params"]

            base_url = f"{WOS_URL}/openscale/{data_mart_id}"
            access_token = get_access_token()

            published_measurements = []
            error_msg = None

            custom_monitoring_run_id = custom_monitor_instance_params["run_details"]["run_id"]

            try:
                status_code, published_measurement = publish_metrics(
                    base_url, access_token, data_mart_id, subscription_id, custom_monitor_id, custom_monitor_instance_id, custom_monitoring_run_id, timestamp
                )
                if int(status_code) in [200, 201, 202]:
                    custom_monitor_instance_params["run_details"]["run_status"] = "finished"
                    published_measurements.append(published_measurement)
                else:
                    custom_monitor_instance_params["run_details"]["run_status"] = "error"
                    custom_monitor_instance_params["run_details"]["run_error_msg"] = published_measurement
                    error_msg = published_measurement

                custom_monitor_instance_params["last_run_time"] = timestamp
                status_code, response = update_monitor_instance(base_url, access_token, custom_monitor_instance_id, custom_monitor_instance_params)

                if not int(status_code) in [200, 201, 202]:
                    error_msg = response

            except Exception as ex:
                error_msg = str(ex)

            if error_msg is None:
                response_payload = {"predictions": [{"values": published_measurements}]}
            else:
                # response_payload = {"error_msg": error_msg}
                response_payload = {"predictions": [{"values": error_msg}]}

            return response_payload

        return publish

    custom_metric_function_name = get_custom_monitor_function_name(custom_monitor_name=config["custom_metric"]["custom_monitor_name"])

    wml.deploy_function(config=config, function=custom_metrics_provider, function_name=custom_metric_function_name, space_type=space_type)


def delete_integrated_system_by_custom_monitor_name(config: dict, log_format: str) -> None:
    """
    Delete integrated system by custom monitor name.

    Args:
        config (dict): configuration dictionary
        log_format (str): log format for this method
    """
    wos_client = config["wos_client"]
    custom_metric_provider_name = get_custom_metric_provider_name(custom_monitor_name=config["custom_metric"]["custom_monitor_name"])
    integrated_systems = get_integrated_systems(config=config)
    if custom_metric_provider_name in integrated_systems:
        _logger.info(f"{log_format} - deleting integrated systems ... {custom_metric_provider_name}")
        ibm_watson_openscale.base_classes.watson_open_scale_v2.IntegratedSystems(wos_client).delete(integrated_system_id=integrated_systems[custom_metric_provider_name], background_mode=False)
        _logger.info(f"{log_format} - delete_integrated_system_by_custom_monitor_name completed.")
    else:
        _logger.info(f"{log_format} - delete_integrated_system_by_custom_monitor_name - Nothing to delete.")


def delete_custom_metric_monitor_by_custom_monitor_name(config: dict, log_format: str) -> None:
    """
    Delete custom metric monitor by custom monitor name.

    Args:
        config (dict): configuration dictionary
        log_format (str): log format for this method
    """
    wos_client = config["wos_client"]
    custom_monitor_name = config["custom_metric"]["custom_monitor_name"]
    monitor_definitions = get_monitor_definitions(config=config)
    if custom_monitor_name in monitor_definitions:
        _logger.info(f"{log_format} - deleting custom metric ... {custom_monitor_name}")
        wos_client.monitor_definitions.delete(monitor_definitions[custom_monitor_name], background_mode=False)
        _logger.info(f"{log_format} - delete_custom_metric_monitor_by_custom_monitor_name completed.")
    else:
        _logger.info(f"{log_format} - delete_custom_metric_monitor_by_custom_monitor_name - Nothing to delete.")


def create_integrated_system(config: dict, space_type: str) -> None:
    """
    Create integrated system.

    Args:
        config (dict): configuration dictionary
        space_type (dict): development or production environment
    """
    wos_client = config["wos_client"]
    wml_client = config["wml_client"]
    custom_monitor_name = config["custom_metric"]["custom_monitor_name"]
    custom_metric_provider_name = get_custom_metric_provider_name(custom_monitor_name=custom_monitor_name)

    CUSTOM_METRICS_PROVIDER_CREDENTIALS = {
        "auth_type": "bearer",
        "token_info": {
            "url": IAM_URL,
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "payload": "grant_type=urn:ibm:params:oauth:grant-type:apikey&response_type=cloud_iam&apikey=" + config["apikey"],
            "method": "POST",
        },
    }

    integrated_systems = get_integrated_systems(config=config)
    if custom_metric_provider_name in integrated_systems:
        ibm_watson_openscale.base_classes.watson_open_scale_v2.IntegratedSystems(wos_client).delete(integrated_system_id=integrated_systems[custom_metric_provider_name], background_mode=False)

    deployments = wml.get_deployment_details(config=config, space_type=space_type)
    custom_monitor_function_name = get_custom_monitor_function_name(custom_monitor_name=custom_monitor_name)
    function_deployment_name = wml.get_function_deployment_name(function_name=custom_monitor_function_name)
    function_deployment_details = deployments[function_deployment_name]

    scoring_url = wml_client.deployments.get_scoring_href(function_deployment_details)
    created_at = function_deployment_details["metadata"]["created_at"]
    current_date = created_at[0 : created_at.find("T")]
    scoring_url = wml_client.deployments.get_scoring_href(function_deployment_details) + "?version=" + current_date

    ibm_watson_openscale.base_classes.watson_open_scale_v2.IntegratedSystems(wos_client).add(
        name=custom_metric_provider_name,
        description=custom_metric_provider_name,
        type="custom_metrics_provider",
        credentials=CUSTOM_METRICS_PROVIDER_CREDENTIALS,
        connection={"display_name": custom_metric_provider_name, "endpoint": scoring_url},
    )


def create_custom_metric_monitor(config: dict) -> None:
    """
    Create custom metric monitor.

    Args:
        config (dict): configuration dictionary
    """
    wos_client = config["wos_client"]
    custom_monitor_name = config["custom_metric"]["custom_monitor_name"]
    metrics = [
        ibm_watson_openscale.base_classes.watson_open_scale_v2.MonitorMetricRequest(
            name="statistical_parity_difference",
            thresholds=[ibm_watson_openscale.base_classes.watson_open_scale_v2.MetricThreshold(type=ibm_watson_openscale.supporting_classes.enums.MetricThresholdTypes.UPPER_LIMIT, default=0.01)],
        ),
        ibm_watson_openscale.base_classes.watson_open_scale_v2.MonitorMetricRequest(
            name="disparate_impact_ratio",
            thresholds=[ibm_watson_openscale.base_classes.watson_open_scale_v2.MetricThreshold(type=ibm_watson_openscale.supporting_classes.enums.MetricThresholdTypes.UPPER_LIMIT, default=0.01)],
        ),
        # ibm_watson_openscale.base_classes.watson_open_scale_v2.MonitorMetricRequest(
        #     name="specificity",
        #     thresholds=[
        #         ibm_watson_openscale.base_classes.watson_open_scale_v2.MetricThreshold(type=ibm_watson_openscale.supporting_classes.enums.MetricThresholdTypes.LOWER_LIMIT, default=0.6),
        #         ibm_watson_openscale.base_classes.watson_open_scale_v2.MetricThreshold(type=ibm_watson_openscale.supporting_classes.enums.MetricThresholdTypes.UPPER_LIMIT, default=1),
        #     ],
        # ),
        # ibm_watson_openscale.base_classes.watson_open_scale_v2.MonitorMetricRequest(
        #     name="sensitivity",
        #     thresholds=[
        #         ibm_watson_openscale.base_classes.watson_open_scale_v2.MetricThreshold(type=ibm_watson_openscale.supporting_classes.enums.MetricThresholdTypes.LOWER_LIMIT, default=0.4),
        #         ibm_watson_openscale.base_classes.watson_open_scale_v2.MetricThreshold(type=ibm_watson_openscale.supporting_classes.enums.MetricThresholdTypes.UPPER_LIMIT, default=1),
        #     ],
        # ),
    ]
    tags = [ibm_watson_openscale.base_classes.watson_open_scale_v2.MonitorTagRequest(name="region", description="us-south")]
    monitor_definitions = get_monitor_definitions(config=config)
    if custom_monitor_name in monitor_definitions:
        wos_client.monitor_definitions.delete(monitor_definitions[custom_monitor_name], background_mode=False)
    wos_client.monitor_definitions.add(name=custom_monitor_name, metrics=metrics, tags=tags, background_mode=False)


def subscribe_custom_model(config: dict, model_config: dict, space_type: str, log_format: str) -> None:
    """
    Subscribe custom model.

    Args:
        config (dict): configuration dictionary
        model_name (str): model name
        space_type (dict): development or production environment
        log_format (str): log format for this method
    """
    model_name = model_config["model_name"]
    _logger.info(f"{log_format} - subscribing custom model ... {model_name}.")

    wos_client = config["wos_client"]
    data_mart_id = config["data_mart_id"]
    service_provider_id = config["custom_service_provider_id"]
    training_file_name = config["training_file_name"]
    subscription_name = get_subscription_name(model_name=model_name, space_type=space_type)
    label_column = model_config["target"]
    scoring_url = model_config["scoring_url"]
    input_data_schema = model_config["input_data_schema"][0]["fields"]

    asset_id = str(uuid.uuid4())
    asset_deployment_id = str(uuid.uuid4())
    scoring_request_headers = {"Content-Type": "application/json"}

    asset = ibm_watson_openscale.supporting_classes.Asset(
        asset_id=asset_id,
        name=subscription_name,
        url="",
        asset_type=ibm_watson_openscale.supporting_classes.enums.AssetTypes.MODEL,
        input_data_type=ibm_watson_openscale.supporting_classes.enums.InputDataType.STRUCTURED,
        problem_type=ibm_watson_openscale.supporting_classes.enums.ProblemType.BINARY_CLASSIFICATION,
    )

    asset_deployment = ibm_watson_openscale.supporting_classes.AssetDeploymentRequest(
        deployment_id=asset_deployment_id,
        name=subscription_name,
        deployment_type=ibm_watson_openscale.supporting_classes.enums.DeploymentTypes.ONLINE,
        scoring_endpoint=ibm_watson_openscale.base_classes.watson_open_scale_v2.ScoringEndpointRequest(url=scoring_url, request_headers=scoring_request_headers),
    )

    training_data_reference = ibm_watson_openscale.supporting_classes.TrainingDataReference(
        type="cos",
        location=ibm_watson_openscale.supporting_classes.COSTrainingDataReferenceLocation(bucket=config["bucket_name"], file_name=training_file_name),
        connection=ibm_watson_openscale.supporting_classes.COSTrainingDataReferenceConnection.from_dict(
            {"resource_instance_id": config["cos_resource_crn"], "url": config["cos_endpoint"], "api_key": config["cos_api_key"], "iam_url": "https://iam.cloud.ibm.com/oidc/token",}
        ),
    )

    feature_columns = [x["name"] for x in input_data_schema]

    cat_features = [x["name"] for x in input_data_schema if x["type"] == "object"]

    training_data_schema = {
        "type": "struct",
        "fields": [{"name": x["name"], "type": "string" if x["type"] == "object" else "long", "nullable": True} for x in input_data_schema],
        "id": "1",
    }

    asset_properties_request = ibm_watson_openscale.supporting_classes.AssetPropertiesRequest(
        label_column=label_column,
        probability_fields=["probability"],
        prediction_field="prediction",
        feature_fields=feature_columns,
        categorical_fields=cat_features,
        training_data_reference=training_data_reference,
        training_data_schema=ibm_watson_openscale.supporting_classes.SparkStruct.from_dict(training_data_schema),
    )

    wos_client.subscriptions.add(
        data_mart_id=data_mart_id, service_provider_id=service_provider_id, asset=asset, deployment=asset_deployment, asset_properties=asset_properties_request, background_mode=False
    )

    _logger.info(f"{log_format} - subscribe_custom_model completed for {model_name}.")


def subscribe_wml_model(config: dict, model_config: dict, space_type: str, log_format: str) -> None:
    """
    Subscribe model.

    Args:
        config (dict): configuration dictionary
        model_name (str): model name
        space_type (dict): development or production environment
        log_format (str): log format for this method
    """
    model_name = model_config["model_name"]
    _logger.info(f"{log_format} - subscribing wml model ... {model_name}.")
    wml_client = config["wml_client"]
    wos_client = config["wos_client"]
    space_id = config["dev_space_id"] if space_type == "dev" else config["prod_space_id"]
    data_mart_id = config["data_mart_id"]
    service_provider_id = config["dev_service_provider_id"] if space_type == "dev" else config["prod_service_provider_id"]
    training_file_name = config["training_file_name"]
    deployment_name = wml.get_model_deployment_name(model_name=model_name)
    subscription_name = get_subscription_name(model_name=model_name, space_type=space_type)
    model_deployments = wml.get_deployments(config=config, space_type=space_type)
    deployment_uid = model_deployments[deployment_name]
    model_details = wml.get_model_details(config=config, space_type=space_type)
    label_column = model_details[model_name]["entity"]["label_column"]

    asset_deployment_details = wos_client.service_providers.list_assets(
        data_mart_id=data_mart_id, service_provider_id=service_provider_id, deployment_id=deployment_uid, deployment_space_id=space_id
    ).result["resources"][0]

    model_asset_details_from_deployment = wos_client.service_providers.get_deployment_asset(
        data_mart_id=data_mart_id, service_provider_id=service_provider_id, deployment_id=deployment_uid, deployment_space_id=space_id
    )

    asset = ibm_watson_openscale.supporting_classes.Asset(
        asset_id=model_asset_details_from_deployment["entity"]["asset"]["asset_id"],
        name=model_asset_details_from_deployment["entity"]["asset"]["name"],
        url=model_asset_details_from_deployment["entity"]["asset"]["url"],
        asset_type=ibm_watson_openscale.supporting_classes.enums.AssetTypes.MODEL,
        input_data_type=ibm_watson_openscale.supporting_classes.enums.InputDataType.STRUCTURED,
        problem_type=ibm_watson_openscale.supporting_classes.enums.ProblemType.BINARY_CLASSIFICATION,
    )

    asset_deployment = ibm_watson_openscale.supporting_classes.AssetDeploymentRequest(
        deployment_id=asset_deployment_details["metadata"]["guid"],
        name=subscription_name,
        deployment_type=ibm_watson_openscale.supporting_classes.enums.DeploymentTypes.ONLINE,
        url=asset_deployment_details["entity"]["scoring_endpoint"]["url"],
        scoring_endpoint=ibm_watson_openscale.base_classes.watson_open_scale_v2.ScoringEndpointRequest(url=wml_client.deployments.get_scoring_href(wml_client.deployments.get_details(deployment_uid))),
    )

    training_data_reference = ibm_watson_openscale.supporting_classes.TrainingDataReference(
        type="cos",
        location=ibm_watson_openscale.supporting_classes.COSTrainingDataReferenceLocation(bucket=config["bucket_name"], file_name=training_file_name),
        connection=ibm_watson_openscale.supporting_classes.COSTrainingDataReferenceConnection.from_dict(
            {"resource_instance_id": config["cos_resource_crn"], "url": config["cos_endpoint"], "api_key": config["cos_api_key"], "iam_url": "https://iam.cloud.ibm.com/oidc/token",}
        ),
    )

    asset_properties_request = ibm_watson_openscale.supporting_classes.AssetPropertiesRequest(
        label_column=label_column,
        probability_fields=["probability"],
        prediction_field="prediction",
        feature_fields=[x["name"] for x in model_asset_details_from_deployment["entity"]["asset_properties"]["input_data_schema"]["fields"]],
        categorical_fields=[x["name"] for x in model_asset_details_from_deployment["entity"]["asset_properties"]["input_data_schema"]["fields"] if x["type"] == "string"],
        training_data_reference=training_data_reference,
        training_data_schema=ibm_watson_openscale.supporting_classes.SparkStruct.from_dict(model_asset_details_from_deployment["entity"]["asset_properties"]["input_data_schema"]),
    )

    wos_client.subscriptions.add(
        data_mart_id=data_mart_id, service_provider_id=service_provider_id, asset=asset, deployment=asset_deployment, asset_properties=asset_properties_request, background_mode=False
    )

    _logger.info(f"{log_format} - subscribe_wml_model completed for {model_name}.")


def subscribe_model(config: dict, model_config: dict, space_type: str, log_format: str) -> None:
    """
    Subscribe model.

    Args:
        config (dict): configuration dictionary
        model_name (str): model name
        space_type (dict): development or production environment
        log_format (str): log format for this method
    """
    model_name = model_config["model_name"]
    _logger.info(f"{log_format} - subscribing model ... {model_name}.")

    if "scoring_url" in model_config:
        subscribe_custom_model(config=config, model_config=model_config, space_type=space_type, log_format=log_format)
    else:
        subscribe_wml_model(config=config, model_config=model_config, space_type=space_type, log_format=log_format)

    _logger.info(f"{log_format} - subscribe_model completed for {model_name}.")


def create_monitor(config: dict, model_name: str, space_type: str, log_format: str):
    """
    Subscribe model.

    Args:
        config (dict): configuration dictionary
        model_name (str): model name
        space_type (dict): development or production environment
        log_format (str): log format for this method
    """

    _logger.info(f"{log_format} - creating monitors ... {model_name}.")
    wos_client = config["wos_client"]
    data_mart_id = config["data_mart_id"]
    monitor_config = config["monitor_config"]
    subscriptions = get_subscriptions(config=config)
    subscription_name = get_subscription_name(model_name=model_name, space_type=space_type)
    subscription_id = subscriptions[subscription_name]

    if "quality" in monitor_config:
        _logger.info(f"{log_format} - creating quality monitor ... {model_name}.")
        wos_client.monitor_instances.create(
            monitor_definition_id=wos_client.monitor_definitions.MONITORS.QUALITY.ID,
            target=ibm_watson_openscale.supporting_classes.Target(target_type=ibm_watson_openscale.supporting_classes.enums.TargetTypes.SUBSCRIPTION, target_id=subscription_id),
            data_mart_id=data_mart_id,
            parameters=monitor_config["quality"]["parameters"],
            thresholds=monitor_config["quality"]["thresholds"],
            background_mode=False,
        )
        _logger.info(f"{log_format} - quality monitor created for {model_name}.")

    if "drift" in monitor_config:
        _logger.info(f"{log_format} - creating drift monitor ... {model_name}.")
        wos_client.monitor_instances.create(
            monitor_definition_id=wos_client.monitor_definitions.MONITORS.DRIFT.ID,
            target=ibm_watson_openscale.supporting_classes.Target(target_type=ibm_watson_openscale.supporting_classes.enums.TargetTypes.SUBSCRIPTION, target_id=subscription_id),
            data_mart_id=data_mart_id,
            parameters=monitor_config["drift"]["parameters"],
            background_mode=False,
        )
        _logger.info(f"{log_format} - drift monitor created for {model_name}.")

    if "fairness" in monitor_config:
        _logger.info(f"{log_format} - creating fairness monitor ... {model_name}.")
        wos_client.monitor_instances.create(
            monitor_definition_id=wos_client.monitor_definitions.MONITORS.FAIRNESS.ID,
            target=ibm_watson_openscale.supporting_classes.Target(target_type=ibm_watson_openscale.supporting_classes.enums.TargetTypes.SUBSCRIPTION, target_id=subscription_id),
            data_mart_id=data_mart_id,
            parameters=monitor_config["fairness"]["parameters"],
            thresholds=monitor_config["fairness"]["thresholds"],
            background_mode=False,
        )
        _logger.info(f"{log_format} - fairness monitor created for {model_name}.")

    if "explainability" in monitor_config:
        _logger.info(f"{log_format} - creating explainability monitor ... {model_name}.")
        wos_client.monitor_instances.create(
            monitor_definition_id=wos_client.monitor_definitions.MONITORS.EXPLAINABILITY.ID,
            target=ibm_watson_openscale.supporting_classes.Target(target_type=ibm_watson_openscale.supporting_classes.enums.TargetTypes.SUBSCRIPTION, target_id=subscription_id),
            data_mart_id=data_mart_id,
            parameters=monitor_config["explainability"]["parameters"],
            background_mode=False,
        )
        _logger.info(f"{log_format} - explainability monitor created for {model_name}.")

    if "custom_metric" in config:
        _logger.info(f"{log_format} - creating custom monitors ... {model_name}.")
        custom_monitor_name = config["custom_metric"]["custom_monitor_name"]
        custom_metric_provider_name = get_custom_metric_provider_name(custom_monitor_name=custom_monitor_name)
        integrated_system_id = get_integrated_systems(config=config)[custom_metric_provider_name]
        custom_monitor_id = get_monitor_definitions(config=config)[custom_monitor_name]
        custom_monitor = {"custom_monitor_id": custom_monitor_id, "parameters": {"custom_metrics_provider_id": integrated_system_id, "custom_metrics_wait_time": 60}}
        wos_client.monitor_instances.create(
            monitor_definition_id=custom_monitor["custom_monitor_id"],
            target=ibm_watson_openscale.supporting_classes.Target(target_type=ibm_watson_openscale.supporting_classes.enums.TargetTypes.SUBSCRIPTION, target_id=subscription_id),
            data_mart_id=data_mart_id,
            parameters=custom_monitor["parameters"],
            background_mode=False,
        )
        _logger.info(f"{log_format} - custom monitors created for {model_name}.")

    wos_client.monitor_instances.create(
        monitor_definition_id=wos_client.monitor_definitions.MONITORS.MODEL_RISK_MANAGEMENT_MONITORING.ID,
        target=ibm_watson_openscale.supporting_classes.Target(target_type=ibm_watson_openscale.supporting_classes.enums.TargetTypes.SUBSCRIPTION, target_id=subscription_id),
        data_mart_id=data_mart_id,
        parameters={},
        managed_by="user",
        background_mode=False,
    )

    _logger.info(f"{log_format} - create_monitor completed for {model_name}.")


def store_feedback(config: dict, model_name: str, feedback_payload: pd.DataFrame, space_type: str, log_format: str):
    """
    Store feedback data.

    Args:
        config (dict): configuration dictionary
        model_name (str): model name
        feedback_payload (pd.DataFrame): feedback payload
        space_type (dict): development or production environment
        log_format (str): log format for this method
    """
    _logger.info(f"{log_format} - storing feedback data ... {model_name}.")
    subscription_name = get_subscription_name(model_name=model_name, space_type=space_type)
    subscriptions = get_subscriptions(config=config)
    subscription_id = subscriptions[subscription_name]
    wos_client = config["wos_client"]
    feedback_dataset_id = (
        wos_client.data_sets.list(
            type=ibm_watson_openscale.supporting_classes.enums.DataSetTypes.FEEDBACK,
            target_target_id=subscription_id,
            target_target_type=ibm_watson_openscale.supporting_classes.enums.TargetTypes.SUBSCRIPTION,
        )
        .result.data_sets[0]
        .metadata.id
    )
    wos_client.data_sets.store_records(feedback_dataset_id, request_body=json.loads(feedback_payload.to_json(orient="records")), background_mode=False)
    _logger.info(f"{log_format} - stored {len(feedback_payload)} records for {model_name}.")
    _logger.info(f"{log_format} - store_feedback completed for {model_name}.")


def store_payload(config: dict, model_config: dict, scoring_payload: pd.DataFrame, space_type: str, log_format: str):
    """
    Store payload data.

    Args:
        config (dict): configuration dictionary
        model_config (dict): model configuraton
        scoring_payload (pd.DataFrame): scoring payload
        space_type (dict): development or production environment
        log_format (str): log format for this method
    """

    model_name = model_config["model_name"]
    _logger.info(f"{log_format} - storing payload data ... {model_name}.")
    subscription_name = get_subscription_name(model_name=model_name, space_type=space_type)
    subscriptions = get_subscriptions(config=config)
    subscription_id = subscriptions[subscription_name]
    wos_client = config["wos_client"]
    scoring_url = model_config["scoring_url"]
    scoring_payload = scoring_payload["input_data"][0]
    payload_data_set_id = (
        wos_client.data_sets.list(
            type=ibm_watson_openscale.supporting_classes.enums.DataSetTypes.PAYLOAD_LOGGING,
            target_target_id=subscription_id,
            target_target_type=ibm_watson_openscale.supporting_classes.enums.TargetTypes.SUBSCRIPTION,
        )
        .result.data_sets[0]
        .metadata.id
    )

    headers = {"Content-Type": "application/json"}
    r = requests.post(scoring_url, data=json.dumps(scoring_payload), headers=headers, verify=False)
    scoring_response = r.json()

    payload_records = [ibm_watson_openscale.supporting_classes.payload_record.PayloadRecord(scoring_id=str(uuid.uuid4()), request=scoring_payload, response=scoring_response, response_time=int(460))]
    wos_client.data_sets.store_records(data_set_id=payload_data_set_id, request_body=payload_records, background_mode=False)
    _logger.info(f"{log_format} - stored {len(scoring_payload['values'])} records for {model_name}.")
    _logger.info(f"{log_format} - store_payload completed for {model_name}.")


def evaluate(config: dict, model_name: str, space_type: str, log_format: str):
    """
    Evaluate model.

    Args:
        config (dict): configuration dictionary
        model_name (str): model name
        space_type (dict): development or production environment
        log_format (str): log format for this method
    """
    _logger.info(f"{log_format} - evaluating ... {model_name}.")
    wos_client = config["wos_client"]
    monitors = get_monitor_instances_by_subscription_name(config=config, model_name=model_name, space_type=space_type)
    mrm_monitor_instance_id = monitors["mrm"]

    evaluation_tests = ["fairness", "quality", "drift"]
    if "custom_metric" in config:
        custom_monitor_name = config["custom_metric"]["custom_monitor_name"]
        custom_metric_name = get_custom_metric_name(custom_monitor_name=custom_monitor_name)
        evaluation_tests.append(custom_metric_name)

    mrm_run_parameters = {"on_demand_trigger": True, "evaluation_tests": evaluation_tests, "publish_fact": "true"}
    wos_client.monitor_instances.run(monitor_instance_id=mrm_monitor_instance_id, triggered_by="user", background_mode=False, parameters=mrm_run_parameters)
    _logger.info(f"{log_format} - evaluate completed for {model_name}.")

