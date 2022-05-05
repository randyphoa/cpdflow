
import pandas as pd
from cpdflow.model.model import get_input_data_schema

df = pd.read_csv("https://raw.githubusercontent.com/randyphoa/cpdflow/main/examples/german_credit_data_biased_training.csv")
target = "Risk"
protected_attributes = ["Age"]
y = df[target]
X = df.drop([target] + protected_attributes, axis=1)

input_data_schema = get_input_data_schema(X=X)
custom_metrics = {"average_precision": 0.9}
