.. _idempotent-operations:

Idempotent Operations
=====================

To ensure idempotent operations, cpdflow performs several checks and depending on the configuration file, could result in 4 outcomes,

1. The asset is updated

2. The asset is overwritten

3. The asset is created

4. No action needs to be done


For example, to **deploy** two models (``German Credit Risk-SVC`` and ``German Credit Risk-RF``) in a development space, using CLI::

   cpdflow apply deploy -c config.json -m "German Credit Risk-SVC" -m "German Credit Risk-RF" -s "dev"

This results in the two models being deployed.

As all cpdflow operations are idempotent, running the above command multiple times, will result in the same outcome. 

In the configuraton file, if ``update`` and ``overwrite`` are set to ``False``, no action will be taken as the models have already been deployed in the earlier step.
