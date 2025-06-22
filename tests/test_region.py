import numpy as np
from world.region import Region
from constants import REGION_SIZE


def test_region_edit_round_trip(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    r = Region.load(0, 0)
    r.height[0, 0] = 5
    r.base[1, 1] = 2
    r.overlay[2, 2] = 3
    r.flags[3, 3] = 4
    r.save()

    loaded = Region.load(0, 0)
    assert np.array_equal(r.height, loaded.height)
    assert np.array_equal(r.base, loaded.base)
    assert np.array_equal(r.overlay, loaded.overlay)
    assert np.array_equal(r.flags, loaded.flags)
