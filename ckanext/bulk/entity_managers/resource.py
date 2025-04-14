from __future__ import annotations

from typing import Any, cast

from sqlalchemy import and_, or_
from sqlalchemy.orm.attributes import InstrumentedAttribute

import ckan.plugins.toolkit as tk
from ckan import model, types
from ckan.lib.dictization import model_dictize

from ckanext.bulk import const
from ckanext.bulk.entity_managers import base


class DatasetResourceEntityManager(base.EntityManager):
    entity_type = "dataset_resource"

    show_action = "resource_show"
    patch_action = "resource_patch"
    delete_action = "resource_delete"

    @classmethod
    def get_fields(cls) -> list[base.FieldItem]:
        if fields := cls.get_fields_from_redis():
            return fields

        fields = [
            base.FieldItem(value=field, text=field)
            for field in model.Resource.get_columns(extra_columns=True)
        ]

        cls.cache_fields_to_redis(fields)

        return fields

    @classmethod
    def search_entities_by_filters(
        cls, filters: list[base.FilterItem], global_operator: str = const.GLOBAL_AND
    ) -> list[dict[str, Any]]:
        """Search for entities by the provided filters.

        Since we are using CKAN resource_search action, we can't support
        all the operators that we have in the frontend.

        TODO: We should add support for more operators in the future.
        """
        supported_operators = [const.OP_IS]

        for f in filters:
            operator = f["operator"]

            if operator not in supported_operators:
                raise ValueError(f"Operator {operator} not supported")

        return cls.resource_search(filters, global_operator)

    @classmethod
    def resource_search(
        cls, filters: list[base.FilterItem], global_operator: str
    ) -> list[dict[str, Any]]:
        """This is a custom version of the core resource_search action.

        Some things we don't need were removed (hash search, term escaping),
        and some things were added (exact search for core fields, working with
        FitlerItem's).

        Note: Due to a Resource's extra fields being stored as a json blob, the
        match is made against the json string representation.  As such, false
        positives may occur:

        If the search criteria is: ::

            query = "field1:term1"

        Then a json blob with the string representation of: ::

            {"field1": "foo", "field2": "term1"}

        will match the search criteria!  This is a known short-coming of this
        approach.
        """
        context: types.Context = cast(
            types.Context,
            {"model": model, "session": model.Session, "user": tk.current_user},
        )

        base_query = model.Session.query(model.Resource).join(model.Package)
        queries = []

        for filter_item in filters:
            if not filter_item["value"]:
                continue

            field = filter_item["field"]
            value = filter_item["value"]

            # TODO: do we need escaping? The interface is available only for
            # sysadmins, so it should be safe.
            # value = misc.escape_sql_like_special_characters(value)

            if field in model.Resource.get_columns():
                queries.append(getattr(model.Resource, field) == value)

            # Resource extras are stored in a json blob.  So searching for
            # matching fields is a bit trickier.
            else:
                model_attr = cast(InstrumentedAttribute, model.Resource.extras)

                queries.append(
                    or_(
                        model_attr.ilike(
                            """%%"%s": "%%%s%%",%%""" % (field, value)  # noqa: UP031
                        ),
                        model_attr.ilike(
                            """%%"%s": "%%%s%%"}""" % (field, value)  # noqa: UP031
                        ),
                    )
                )

        if not queries:
            return []

        op_func = and_ if global_operator == const.GLOBAL_AND else or_
        base_query = base_query.filter(op_func(*queries))

        return model_dictize.resource_list_dictize(list(base_query), context)
