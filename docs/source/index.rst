.. |br| raw:: html

   <br />


|br|

.. image:: _static/logo.png
   :align: center
   :alt: cpdflow

|br|


cpdflow is a declarative approach to model lifecycle management on Cloud Pak for Data.

In a nutshell, cpdflow consolidates APIs from various Cloud Pak for Data modules in a dependency graph aligned to the 4 model lifecycle stages from `Factsheets Model Inventory <https://dataplatform.cloud.ibm.com/docs/content/wsj/analyze-data/factsheets-model-inventory.html>`_; so that you can simply declare the end state of each model and cpdflow infers the necessary steps and runs them.

Think of it as using *Kubernete's apply* to manage model lifecycles. 
Simply declare the final :ref:`lifecycle stage <lifecycle-stages>` for each model and let cpdflow handle the rest. 

For example, to **deploy** two models (``German Credit Risk-SVC`` and ``German Credit Risk-RF``) in the development space, simply define the model names in the respective lifecycle stage::

   cpdflow apply deploy -c config.json -m "German Credit Risk-SVC" -m "German Credit Risk-RF" -s "dev"

And to **validate** another model (``German Credit Risk-GBC``) on OpenScale in a development environment::

   cpdflow apply validate -c config.json -m "German Credit Risk-GBC"

.. note:: 
   Although there are prerequisites steps such as training, deploying and subscribing before OpenScale can evaluate the model, it was not explictly defined as cpdflow handles dependencies automatically.


cpdflow infers the necessary steps that needs to be actioned upon to achieve the final state.

Under the hood, cpdflow generates an execution path based on a :ref:`dependency graph <dependency-graph>` and runs the necessary steps to achieve the model's desired lifecycle stage.


Here is what the entire graph looks like,

.. image:: _static/graph.png
   :alt: Graph

|br|

This is a living graph and is updated consistently to add new features and API changes.

|br|

.. toctree::
   :caption: Overview
   :maxdepth: 1

   Lifecycle Stages <lifecycle_stages>
   Dependency Graph <dependency_graph>
   Idempotent Operations <idempotent_operations>


.. .. toctree::
..    :caption: Under the hood
..    :maxdepth: 1

..    How It Works <how_it_works>
..    Dependency Graph <dependency_graph>
..    Idempotent Operations <idempotent_operations>


.. toctree::
   :caption: Getting Started
   :maxdepth: 1

   Installation <installation>
   Usage <usage>

.. toctree::
   :caption: Examples
   :maxdepth: 1

   examples/german_credit_risk.ipynb


.. toctree::
   :caption: Configurations
   :maxdepth: 1

   Configuration File <config_file>
   Model Configuration <config_model>


.. toctree::
   :caption: API Reference
   :maxdepth: 1

   API Reference <api>


cpdflow
=======