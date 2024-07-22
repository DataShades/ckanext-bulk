"""Tests for ckanext.bulk.plugin.

There is nothing to test here. But you can add tests for implementations into
this file. Or wait till some functionality is added to this plugin

Just as an example, we are testing that plugin can be loaded. This test has no
real value, because a lot of other tests will load the plugin implicitely, thus
we'd notice if something is broken anyway.
"""

import pytest

from ckan.plugins import plugin_loaded


@pytest.mark.usefixtures("with_plugins")
def test_plugin():
    """Plugin bulk is enabled in config."""
    assert plugin_loaded("bulk")
