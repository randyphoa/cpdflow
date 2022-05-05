"""
The 4 model lifecycle stages from AI Governance Factsheets.
1. Develop
2. Deploy
3. Validate
4. Operate
"""

from cpdflow.lifecycle.develop import develop

from cpdflow.lifecycle.deploy import deploy

from cpdflow.lifecycle.subscribe import validate, operate


class apply:
    """
    Handle apply commands.
    """

    @staticmethod
    def develop(config: dict, model_names: list) -> None:
        develop.apply(config=config, model_names=model_names)

    @staticmethod
    def deploy(config: dict, model_names: list, space_type: str) -> None:
        deploy.apply(config=config, model_names=model_names, space_type=space_type)

    @staticmethod
    def validate(config: dict, model_names: list) -> None:
        validate.apply(config=config, model_names=model_names)

    @staticmethod
    def operate(config: dict, model_names: list) -> None:
        operate.apply(config=config, model_names=model_names)


class delete:
    """
    Handle delete commands.
    """

    @staticmethod
    def develop(config: dict, model_names: list) -> None:
        develop.delete(config=config, model_names=model_names)

    @staticmethod
    def deploy(config: dict, model_names: list, space_type: str) -> None:
        deploy.delete(config=config, model_names=model_names, space_type=space_type)

    @staticmethod
    def validate(config: dict, model_names: list) -> None:
        validate.delete(config=config, model_names=model_names)

    @staticmethod
    def operate(config: dict, model_names: list) -> None:
        operate.delete(config=config, model_names=model_names)
