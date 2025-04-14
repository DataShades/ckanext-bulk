from __future__ import annotations

from ckanext.bulk.entity_managers.group import GroupEntityManager


class OrganizationEntityManager(GroupEntityManager):
    entity_type = "organization"

    list_action = "organization_list"
    show_action = "organization_show"
    patch_action = "organization_patch"
    delete_action = "organization_delete"
