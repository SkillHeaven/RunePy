import numpy as np
from runepy.world import Region
from constants import REGION_SIZE


def test_region_round_trip(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    r1 = Region.load(0, 0)
    assert r1.height.shape == (REGION_SIZE, REGION_SIZE)
    r1.height[1, 1] = 5
    r1.base[2, 2] = 3
    r1.overlay[3, 3] = 4
    r1.flags[4, 4] = 7
    r1.save()

    r2 = Region.load(0, 0)
    assert np.array_equal(r1.height, r2.height)
    assert np.array_equal(r1.base, r2.base)
    assert np.array_equal(r1.overlay, r2.overlay)
    assert np.array_equal(r1.flags, r2.flags)
