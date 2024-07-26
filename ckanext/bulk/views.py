from __future__ import annotations

from flask import Blueprint
from flask.views import MethodView

import ckan.plugins.toolkit as tk

__all__ = ["bp"]

bp = Blueprint("bulk", __name__, url_prefix="/bulk")


@bp.errorhandler(tk.NotAuthorized)
def not_authorized_handler(_: tk.NotAuthorized) -> tuple[str, int]:
    """Generic handler for NotAuthorized exception."""
    return (
        tk.render(
            "bulk/error.html",
            {
                "code": 403,
                "content": "Not authorized to view this page",
                "name": "Not authorized",
            },
        ),
        403,
    )


def create_filter_item() -> str:
    return tk.render("bulk/snippets/filter_item.html", {"data": {}, "errors": {}})


def create_update_item() -> str:
    return tk.render("bulk/snippets/update_item.html", {"data": {}, "errors": {}})


class BulkManagerView(MethodView):
    template = "bulk/manager.html"

    def get(self):
        tk.check_access("bulk_manager", {})

        return tk.render(self.template, {"data": {}, "errors": {}})

    def post(self):
        # params = parse_params(tk.request.form)

        return tk.redirect_to("bulk.manager")


bp.add_url_rule("/manager", view_func=BulkManagerView.as_view("manager"))
bp.add_url_rule("/htmx/create_filter_item", view_func=create_filter_item)
bp.add_url_rule("/htmx/create_update_item", view_func=create_update_item)
