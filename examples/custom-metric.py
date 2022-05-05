def calculate_metrics(df):
    from aif360.sklearn.metrics import disparate_impact_ratio, statistical_parity_difference

    dir = disparate_impact_ratio(df[["Sex", "_original_prediction"]].copy().set_index("Sex"), prot_attr=["Sex"], priv_group="male", pos_label="Risk")

    spd = statistical_parity_difference(df[["Sex", "_original_prediction"]].copy().set_index("Sex"), prot_attr=["Sex"], priv_group="male", pos_label="Risk")

    metrics = {
        "statistical_parity_difference": spd, 
        "disparate_impact_ratio": dir, 
        "region": "us-south"
    }

    return metrics
