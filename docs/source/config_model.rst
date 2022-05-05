Model Configuration File
========================

From the configuraton file, below is an example of the contents in ``german-credit-risk-sgd.py``.

.. code-block:: python

    "models": {
        "model_configs": [
            {
                "model_name": "German Credit Risk-SGD", 
                "model_script": "german-credit-risk-sgd.py", 
                "update": True, 
                "overwrite": True
            },
        ]
    },


Contents of ``german-credit-risk-sgd.py``.

.. code-block:: python

    import pandas as pd
    from sklearn.compose import ColumnTransformer
    from sklearn.linear_model import SGDClassifier
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder, StandardScaler
    from cpdflow.model.model import get_input_data_schema

    # Train model
    df = pd.read_csv("german_credit_data_biased_training.csv")
    target = "Risk"
    protected_attributes = ["Age"]
    y = df[target]
    X = df.drop([target] + protected_attributes, axis=1)
    ct = ColumnTransformer([("ohe", OneHotEncoder(), X.select_dtypes(include=["object"]).columns.tolist())])
    scaler = StandardScaler(with_mean=False)

    model = Pipeline([("ct", ct), ("scaler", scaler), ("clf", SGDClassifier(loss="modified_huber"))]).fit(X, y)
    
    input_data_schema = get_input_data_schema(X=X)

    custom_metrics = {
        "average_precision": 0.0 # add custom metrics if needed
    }

.. note:: 
   The 3 required variables from the model script are,

   1. ``target`` - Label name.


   2. ``model`` - A fitted/trained model that is ready to be inferred.
   

   3. ``input_data_schema`` - A list of fields that is used for training.
   
   

