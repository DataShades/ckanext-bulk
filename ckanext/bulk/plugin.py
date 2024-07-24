from __future__ import annotations

import ckan.plugins as p
import ckan.plugins.toolkit as tk
from ckan.common import CKANConfig


@tk.blanket.actions
@tk.blanket.auth_functions
@tk.blanket.blueprints
@tk.blanket.cli
@tk.blanket.config_declarations
@tk.blanket.helpers
@tk.blanket.validators
class BulkPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer)

    # IConfigurer
    def update_config(self, config_: CKANConfig):
        """Modify CKAN configuration."""
        # register templates of the plugin
        tk.add_template_directory(config_, "templates")

        # every file from the public directory can be accessed directly from
        # the browser. Use this for public images, site logos, downloadable
        # documents.
        tk.add_public_directory(config_, "public")

        # register assets folder. You must add `webassets.yml` into this folder
        tk.add_resource("assets", "bulk")
