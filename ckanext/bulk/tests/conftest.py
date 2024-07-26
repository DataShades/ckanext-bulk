from __future__ import annotations

import pytest

from ckanext.bulk.entity_manager import (
    DatasetEntityManager,
    DatasetResourceEntityManager,
    GroupEntityManager,
    OrganizationEntityManager,
)


@pytest.fixture()
def group_entity_manager():
    return GroupEntityManager


@pytest.fixture()
def organization_entity_manager():
    return OrganizationEntityManager


@pytest.fixture()
def dataset_entity_manager():
    return DatasetEntityManager


@pytest.fixture()
def dataset_resource_entity_manager():
    return DatasetResourceEntityManager
