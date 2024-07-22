"""Benchmarks for bulk plugin.

Write benchmarks here while developing new features and remove them after the
solution is stabilized.

Benchmarks can be kept, but if you are not comparing results of different
versions of code, running benchmarks is just a waste of resources.

To run benchmark, just pass the tested function into `benchmark` fixture. If
function accepts arguments, add them as extra parameters for benchmark fixture.

Example:
    def test_something(benchmark):
        benchmark(my_function, arg1, arg2)
"""

from __future__ import annotations

from typing import Any

import pytest

from ckan.plugins import plugin_loaded


@pytest.mark.benchmark()
@pytest.mark.usefixtures("with_plugins")
def test_plugin(benchmark: Any):
    """First version of code."""
    benchmark(plugin_loaded, "bulk")


@pytest.mark.benchmark()
@pytest.mark.usefixtures("with_plugins")
def test_plugin_with_spaces(benchmark: Any):
    """Second version of code."""
    benchmark(plugin_loaded, " bulk ")
