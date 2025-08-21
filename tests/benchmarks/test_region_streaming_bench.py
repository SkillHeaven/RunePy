"""Benchmark region loading with and without caching.

This benchmark uses ``pytest-benchmark`` to compare loading the same region
multiple times directly versus loading through ``RegionManager`` which caches
previously loaded regions in memory.
"""

import pytest

from runepy.world.manager import RegionManager
from runepy.world.region import Region

pytest.importorskip("pytest_benchmark")


def _prepare_region(tmp_path):
    region = Region.load(0, 0)
    region.save()


def test_region_loading_uncached(benchmark, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _prepare_region(tmp_path)
    benchmark(lambda: Region.load(0, 0))


def test_region_loading_cached(benchmark, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _prepare_region(tmp_path)
    mgr = RegionManager()
    mgr.load_region(0, 0)  # populate cache
    mgr.unload_region(0, 0)
    benchmark(lambda: mgr.load_region(0, 0))
