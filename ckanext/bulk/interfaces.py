from __future__ import annotations

from typing import Any

from ckan.plugins import Interface

from ckanext.bulk.entity_managers import (
    base,
    DatasetEntityManager,
    DatasetResourceEntityManager,
    GroupEntityManager,
    OrganizationEntityManager,
)


class IBulk(Interface):
    def register_entity_manager(
        self, default_entity_managers: dict[str, type[base.EntityManager]]
    ) -> dict[str, type[base.EntityManager]]:
        """Register entity manager.

        This methods allows you to register your own entity managers or
        override the default ones.

        Args:
            default_entity_managers: Default entity managers.

        Returns:
            Registered entity managers.
        """
        return default_entity_managers

    def prepare_csv_data(
        self,
        data: list[dict[str, Any]],
        export_type: str,
        entity_type: str | None = None,
    ) -> list[dict[str, Any]]:
        """Prepare CSV data.

        It might be search results or logs.

        This method allows you to prepare CSV data for export.
        You can use this method to add/remove/update fields from the data.

        Args:
            data: Data to prepare.
            export_type: Type of data (result or logs).
            entity_type: Type of entity, available only for search result export.

        Returns:
            Prepared data.
        """
        if export_type == "result":
            new_data = []

            field_mappings = {
                DatasetEntityManager.entity_type: (
                    "id",
                    "name",
                    "title",
                    "notes",
                    "metadata_modified",
                    "metadata_created",
                    "state",
                    "type",
                    "num_resources",
                    "owner_org",
                    "license_id",
                ),
                DatasetResourceEntityManager.entity_type: (
                    "id",
                    "name",
                    "package_id",
                    "format",
                    "private",
                    "created",
                    "last_modified",
                    "datastore_active",
                    "size",
                    "url",
                ),
                GroupEntityManager.entity_type: (
                    "id",
                    "name",
                    "title",
                    "description",
                    "is_organization",
                ),
                OrganizationEntityManager.entity_type: (
                    "id",
                    "name",
                    "title",
                    "description",
                    "is_organization",
                ),
            }

            for record in data:
                if entity_type not in field_mappings:
                    continue

                new_data.append(
                    {
                        field: record.get(field, "")
                        for field in field_mappings[entity_type]
                    }
                )

            return new_data

        elif export_type == "logs":
            for record in data:
                record["result"] = True if record["result"] else False

            return data

        return data
