from __future__ import annotations

from ckan.plugins import Interface

from ckanext.bulk.entity_managers import base


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
