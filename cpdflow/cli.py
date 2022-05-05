"""
Command line interface methods.
"""

import json
import click
import logging
import cpdflow

_logger = logging.getLogger(__name__)


@click.group()
def cli():
    pass


# @cli.group()
# def wp():
#     pass

# @wp.command("install")
# def wp_install():
#     print("wp install")


@cli.group()
def delete():
    """
    Delete assets in specified lifecycle stage.
    """
    pass


@cli.group()
def apply():
    """
    Update, overwrite or create assets in specified lifecycle stage.
    """
    pass


@click.option("--config", "-c", type=str, default="config.json", help="path to configuration file")
@click.option("--model", "-m", type=str, multiple=True, help="name of model")
@delete.command("develop")
def delete_develop(config, model):
    """
    Delete model and its depedencies.
    """
    with open(config) as f:
        config = json.load(f)
    
    config = cpdflow.init_config(config=config)
    cpdflow.delete.develop(config=config, model_names=list(model))


@click.option("--config", "-c", type=str, default="config.json", help="path to configuration file")
@click.option("--model", "-m", type=str, multiple=True, help="name of model")
@apply.command("develop")
def apply_develop(config, model):
    """
    Run and store model in project space with Factsheets.
    """
    with open(config) as f:
        config = json.load(f)
    config = cpdflow.init_config(config=config)
    cpdflow.apply.develop(config=config, model_names=list(model))


@click.option("--config", "-c", type=str, default="config.json", help="path to configuration file")
@click.option("--model", "-m", type=str, multiple=True, help="name of model")
@click.option("--space", "-s", type=str, help="deployment space")
@delete.command("deploy")
def delete_deploy(config, model, space):
    """
    Delete model deployment and its depedencies.
    """
    with open(config) as f:
        config = json.load(f)
    config = cpdflow.init_config(config=config)
    cpdflow.delete.deploy(config=config, model_names=list(model), space_type=space)


@click.option("--config", "-c", type=str, default="config.json", help="path to configuration file")
@click.option("--model", "-m", type=str, multiple=True, help="name of model")
@click.option("--space", "-s", type=str, help="deployment space")
@apply.command("deploy")
def apply_deploy(config, model, space):
    """
    Promote and deploy model to the specified environment.
    """
    with open(config) as f:
        config = json.load(f)
    config = cpdflow.init_config(config=config)
    cpdflow.apply.deploy(config=config, model_names=list(model), space_type=space)


@click.option("--config", "-c", type=str, default="config.json", help="path to configuration file")
@click.option("--model", "-m", type=str, multiple=True, help="name of model")
@delete.command("validate")
def validate(config, model):
    """
    Delete subscription in OpenScale development environment.
    """
    cpdflow.delete.validate(config=config, model_names=list(model))

@click.option("--config", "-c", type=str, default="config.json", help="path to configuration file")
@click.option("--model", "-m", type=str, multiple=True, help="name of model")
@apply.command("validate")
def validate(config, model):
    """
    Subscribe and evaluate model in OpenScale development environment.
    """
    cpdflow.apply.validate(config=config, model_names=list(model))


@click.option("--config", "-c", type=str, default="config.json", help="path to configuration file")
@click.option("--model", "-m", type=str, multiple=True, help="name of model")
@delete.command("operate")
def operate(config, model):
    """
    Delete subscription in OpenScale production environment.
    """
    cpdflow.delete.operate(config=config, model_names=list(model))

@click.option("--config", "-c", type=str, default="config.json", help="path to configuration file")
@click.option("--model", "-m", type=str, multiple=True, help="name of model")
@apply.command("operate")
def operate(config, model):
    """
    Subscribe and evaluate model in OpenScale production environment.
    """
    cpdflow.apply.operate(config=config, model_names=list(model))

if __name__ == "__main__":
    cli()
