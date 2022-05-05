.. _config-file:

Configuration File
==================


Python Dictionary
-----------------

An example of the configuration file in Python dictionary.

.. code-block:: python

    {
        "platform": {"apikey": "", "url": "https://us-south.ml.cloud.ibm.com"},
        "ws": {"project_name": "Demo"},
        "wml": {"dev_space": "Dev Space 3", "prod_space": "Prod Space"},
        "wkc": {"catalog_name": "My Catalog", "model_entry_name": "German Credit Risk Model", "model_entry_description": "German Credit Risk Model Description"},
        "cos": {
            "cos_api_key": "",
            "cos_resource_crn": "crn:v1:bluemix:public:iam-identity::a/53be0036a6fd4cdd9f4caca09dbcb6c9::serviceid:ServiceId-07cbf50f-45ec-4dfc-85b4-ea9fb3ce614f",
            "cos_endpoint": "https://s3.us.cloud-object-storage.appdomain.cloud",
            "bucket_name": "sony-data-store",
            "training_file_name": "german_credit_data_biased_training.csv",
        },
        "wos": {
            "data_mart_id": "0adabc21-cf18-48c0-a36c-f7e3f3b092e8",
            "dev_service_provider": "WML - Dev",
            "prod_service_provider": "WML - Prod",
            "custom_service_provider": "Custom WML Provider",
            "custom_metric": {"custom_monitor_name": "Custom Metrics", "custom_metric_script": "custom-metric.py", "overwrite": True,},
            "scoring_payload": {"file_name": "german_credit_risk_scoring.csv"},
            "meta_payload": {"file_name": "german_credit_risk_meta.csv"},
            "feedback_payload": {"file_name": "german_credit_risk_feedback.csv"},
            "monitor_config": {
                "quality": {
                    "parameters": {"min_feedback_data_size": 50}, 
                    "thresholds": [{"metric_id": "area_under_roc", "type": "lower_limit", "value": 0.9}]
                },
                "drift": {
                    "parameters": {"min_samples": 100, "drift_threshold": 0.1, "train_drift_model": True, "enable_model_drift": False, "enable_data_drift": True}
                },
                "fairness": {
                    "parameters": {
                        "features": [{"feature": "Sex", "majority": ["male"], "minority": ["female"], "threshold": 0.95}, {"feature": "Age", "majority": [[26, 75]], "minority": [[18, 25]]}],
                        "favourable_class": ["No Risk"],
                        "unfavourable_class": ["Risk"],
                        "min_records": 100,
                    },
                    "thresholds": [
                        {"metric_id": "fairness_value", "specific_values": [{"applies_to": [{"type": "tag", "value": "Age", "key": "feature"}], "value": 80}], "type": "lower_limit", "value": 80}
                    ],
                },
                "explainability": {"parameters": {"enabled": True}},
            },
        },
        "models": {
            "model_configs": [
                {"model_name": "German Credit Risk-SGD", "model_script": "german-credit-risk-sgd.py", "update": True, "overwrite": True},
                {"model_name": "German Credit Risk-RF", "model_script": "german-credit-risk-rf.py", "update": True, "overwrite": True},
                {"model_name": "German Credit Risk-SVC", "model_script": "german-credit-risk-svc.py", "update": True, "overwrite": True},
                {"model_name": "German Credit Risk-GBC", "model_script": "german-credit-risk-gbc.py", "update": True, "overwrite": True},
                {
                    "model_name": "German Credit Risk-custom",
                    "model_script": "german-credit-risk-custom.py",
                    "scoring_url": "http://ml-provider-ml.itzroks-550003aw18-xko3n2-6ccd7f378ae819553d37d5f2ee142bd6-0000.au-syd.containers.appdomain.cloud/predict",
                    "update": True,
                    "overwrite": True,
                },
            ]
        },
    }




Json
----

An example of the configuration file in Json.

.. code-block:: json

    {
        "platform": {
            "apikey": "",
            "url": "https://us-south.ml.cloud.ibm.com"
        },
        "ws": {
            "project_name": "Demo"
        },
        "wml": {
            "dev_space": "Dev Space",
            "prod_space": "Prod Space"
        },
        "wkc": {
            "catalog_name": "My Catalog",
            "model_entry_name": "German Credit Risk Model",
            "model_entry_description": "German Credit Risk Model Description"
        },
        "cos": {
            "cos_api_key": "",
            "cos_resource_crn": "crn:v1:bluemix:public:iam-identity::a/53be0036a6fd4cdd9f4caca09dbcb6c9::serviceid:ServiceId-07cbf50f-45ec-4dfc-85b4-ea9fb3ce614f",
            "cos_endpoint": "https://s3.us.cloud-object-storage.appdomain.cloud",
            "bucket_name": "sony-data-store",
            "training_file_name": "german_credit_data_biased_training.csv"
        },
        "wos": {
            "data_mart_id": "0adabc21-cf18-48c0-a36c-f7e3f3b092e8",
            "dev_service_provider": "WML - Dev",
            "prod_service_provider": "WML - Prod",
            "custom_service_provider": "Custom WML Provider",
            "custom_metric": {
                "custom_monitor_name": "Custom Metrics",
                "custom_metric_script": "custom-metric.py",
                "overwrite": true
            },
            "scoring_payload": {
                "file_name": "german_credit_risk_scoring.csv"
            },
            "meta_payload": {
                "file_name": "german_credit_risk_meta.csv"
            },
            "feedback_payload": {
                "file_name": "german_credit_risk_feedback.csv"
            },
            "monitor_config": {
                "quality": {
                    "parameters": {
                        "min_feedback_data_size": 50
                    },
                    "thresholds": [
                        {
                            "metric_id": "area_under_roc",
                            "type": "lower_limit",
                            "value": 0.9
                        }
                    ]
                }
            }
        },
        "models": {
            "model_configs": [
                {
                    "model_name": "German Credit Risk-SGD",
                    "model_script": "german-credit-risk-sgd.py",
                    "update": true,
                    "overwrite": true
                },
                {
                    "model_name": "German Credit Risk-RF",
                    "model_script": "german-credit-risk-rf.py",
                    "update": true,
                    "overwrite": true
                },
                {
                    "model_name": "German Credit Risk-SVC",
                    "model_script": "german-credit-risk-svc.py",
                    "update": true,
                    "overwrite": true
                },
                {
                    "model_name": "German Credit Risk-GBC",
                    "model_script": "german-credit-risk-gbc.py",
                    "update": true,
                    "overwrite": true
                },
                {
                    "model_name": "German Credit Risk-custom",
                    "model_script": "german-credit-risk-custom.py",
                    "scoring_url": "http://ml-provider-ml.itzroks-550003aw18-xko3n2-6ccd7f378ae819553d37d5f2ee142bd6-0000.au-syd.containers.appdomain.cloud/predict",
                    "update": true,
                    "overwrite": true
                }
            ]
        }
    }