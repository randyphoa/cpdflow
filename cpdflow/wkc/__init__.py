"""
Watson Knowledge Catalog APIs.
"""

from .wkc import (
    get_catalogs,
    get_model_entry_details,
    get_model_entry_details_by_model_entry_name,
    delete_model_from_inventory_by_model_names,
    delete_model_from_project_inventory_by_model_names,
    export_facts,
    register_model_existing_entry,
    register_model_new_entry,
    register_model,
    register_model_from_project,
)

