from __future__ import annotations

from ckan import plugins as p

from ckanext.bulk.entity_managers import (
    DatasetEntityManager,
    DatasetResourceEntityManager,
    GroupEntityManager,
    OrganizationEntityManager,
    base,
)
from ckanext.bulk.interfaces import IBulk


def get_entity_managers() -> dict[str, type[base.EntityManager]]:
    """Get all the registered entity managers.

    Returns:
        A dictionary of entity type to entity manager.
    """
    default_entity_managers = {
        manager.entity_type: manager
        for manager in [
            DatasetEntityManager,
            DatasetResourceEntityManager,
            OrganizationEntityManager,
            GroupEntityManager,
        ]
    }

    for plugin in p.PluginImplementations(IBulk):
        default_entity_managers.update(
            plugin.register_entity_manager(default_entity_managers)
        )

    return default_entity_managers


def get_entity_manager(entity_type: str) -> type[base.EntityManager]:
    """Get the entity manager for the given entity type.

    Args:
        entity_type: The type of the entity to get the manager for.

    Returns:
        The entity manager for the given entity type.

    Raises:
        EntityMissingError: If the entity manager for the given entity type is
            not found.
    """
    if manager := get_entity_managers().get(entity_type):
        return manager

    raise base.EntityMissingError(entity_type)
