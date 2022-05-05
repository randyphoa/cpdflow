"""
cpdflow is a declarative approach to model lifecycle management on Cloud Pak for Data.
"""

from cpdflow.config import init_config
from cpdflow.lifecycle import apply, delete
from cpdflow.utils.logging_utils import _configure_loggers
from cpdflow.version import __version__

_configure_loggers(root_module_name=__name__)
