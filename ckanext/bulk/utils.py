from __future__ import annotations

from typing import Any

from cachelib.redis import RedisCache
from redis.connection import parse_url

import ckan.plugins.toolkit as tk
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


def store_data(key: str, data: Any, ttl: int = 3600) -> None:
    """Store result/logs data in redis.

    Args:
        key: The key to store the data in redis.
        data: The data to store in redis.
        ttl: The time to live for the data in redis.
    """
    parsed_url = parse_url(tk.config["ckan.redis.url"])
    cache = RedisCache(
        host=parsed_url["host"],
        port=parsed_url["port"],
        password=parsed_url.get("password", ""),
        default_timeout=ttl,
    )
    cache.set(key, data)


def get_data(key: str) -> Any | None:
    """Get data from redis.

    Args:
        key: The key to get the data from redis.

    Returns:
        The data stored in redis for the given key, or None if not found.
    """
    parsed_url = parse_url(tk.config["ckan.redis.url"])
    cache = RedisCache(
        host=parsed_url["host"],
        port=parsed_url["port"],
        password=parsed_url.get("password", ""),
    )
    return cache.get(key)
