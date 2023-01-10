<p>
  <b>
    This project has been superseded by <a href="https://github.com/crossdeploy-io/crossdeploy" title="crossdeploy">crossdeploy</a>.
  </b>
</p>

---

<p align="center">
  <img src="https://cpdflow.readthedocs.io/en/latest/_images/logo.png" alt="cpdflow" />
</p>

---

cpdflow is a declarative approach to model lifecycle management on Cloud Pak for Data.

In a nutshell, cpdflow consolidates APIs from various Cloud Pak for Data modules in a dependency graph aligned to the 4 model lifecycle stages from [Factsheets Model Inventory](https://dataplatform.cloud.ibm.com/docs/content/wsj/analyze-data/factsheets-model-inventory.html); so that you can simply declare the end state of each model and cpdflow infers the necessary steps and runs them.

Think of it as using *Kubernete's apply* to manage model lifecycles. Simply declare the final [lifecycle stage](https://cpdflow.readthedocs.io/en/latest/lifecycle_stages.html#lifecycle-stages) for each model and let cpdflow handle the rest. 

For example, to **deploy** two models (`German Credit Risk-SVC` and `German Credit Risk-RF`) in a development space, simply define the model names in the respective lifecycle stage.
```
cpdflow apply deploy -c config.json -m "German Credit Risk-SVC" -m "German Credit Risk-RF"
```

And to **validate** another model (`German Credit Risk-GBC`) on OpenScale in a development environment.
```
cpdflow apply validate -c config.json -m "German Credit Risk-GBC"
```

**Note**: Although there are prerequisites steps such as training, deploying and subscribing before OpenScale can evaluate the model, it was not explictly defined as cpdflow handles dependencies automatically.

cpdflow infers the necessary steps that needs to be actioned upon to achieve the final state.

Under the hood, cpdflow generates an execution path based on a [dependency graph](https://cpdflow.readthedocs.io/en/latest/dependency_graph.html) and runs the necessary steps to achieve the model's desired lifecycle stage.

Here is what the entire graph looks like,

![Graph](https://cpdflow.readthedocs.io/en/latest/_images/graph.png)

This is a living graph and is updated consistently to add new features and update API changes.
