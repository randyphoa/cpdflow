
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from cpdflow.model.model import get_input_data_schema

df = pd.read_csv("https://raw.githubusercontent.com/randyphoa/cpdflow/main/examples/german_credit_data_biased_training.csv")
target = "Risk"
protected_attributes = ["Age"]
y = df[target]
X = df.drop([target] + protected_attributes, axis=1)
ct = ColumnTransformer([("ohe", OneHotEncoder(), X.select_dtypes(include=["object"]).columns.tolist())])
scaler = StandardScaler(with_mean=False)

model = Pipeline([("ct", ct), ("scaler", scaler), ("clf", SVC(probability=True))]).fit(X, y)
input_data_schema = get_input_data_schema(X=X)
custom_metrics = {
    "average_precision": 0.9
}
