import numpy as np
from runepy.world.manager import RegionManager
from runepy.world.region import Region
from constants import REGION_SIZE


def test_region_manager_loading(tmp_path, monkeypatch):
    # Ensure regions are stored in temporary directory
    monkeypatch.chdir(tmp_path)

    mgr = RegionManager(view_radius=1)
    # initial position inside region (0,0)
    mgr.ensure(10, 10)
    assert len(mgr.loaded) == 9  # 3x3 window

    # move east across region boundary
    mgr.ensure(REGION_SIZE + 1, 10)
    assert (1, 0) in mgr.loaded
    assert len(mgr.loaded) <= 9
    assert (-1, 0) not in mgr.loaded

    # move north across boundary
    mgr.ensure(REGION_SIZE + 1, REGION_SIZE + 2)
    assert (1, 1) in mgr.loaded
    assert len(mgr.loaded) <= 9
    assert (0, -1) not in mgr.loaded



def test_clear_cache(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    mgr = RegionManager(view_radius=1)
    mgr.ensure(0, 0)
    assert mgr._cache
    mgr.clear_cache()
    assert mgr._cache == {}
