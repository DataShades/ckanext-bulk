from __future__ import annotations

import pytest

import ckan.plugins as p

from ckanext.bulk import utils
from ckanext.bulk.entity_managers import DatasetEntityManager, base
from ckanext.bulk.interfaces import IBulk


class CustomEntityManager(base.EntityManager):
    entity_type = "custom"


class TestBulkPlugin(p.SingletonPlugin):
    p.implements(IBulk)

    def register_entity_manager(
        self, entity_managers: dict[str, type[base.EntityManager]]
    ) -> dict[str, type[base.EntityManager]]:
        entity_managers[CustomEntityManager.entity_type] = CustomEntityManager
        entity_managers[DatasetEntityManager.entity_type] = CustomEntityManager

        return entity_managers


@pytest.mark.ckan_config("ckan.plugins", "bulk test_bulk_plugin")
@pytest.mark.usefixtures("non_clean_db", "with_plugins")
class TestBulkInterace:
    def test_register_new_entity_manager(self):
        assert (
            utils.get_entity_manager(CustomEntityManager.entity_type)
            is CustomEntityManager
        )

    def test_replace_existing_entity_manager(self):
        assert (
            utils.get_entity_manager(DatasetEntityManager.entity_type)
            is CustomEntityManager
        )
