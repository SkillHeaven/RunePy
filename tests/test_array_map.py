import os

import numpy as np

from runepy.array_map import RegionArrays


def test_regionarrays_save_load(tmp_path):
    region = RegionArrays.empty(shape=(4, 4))
    region.height_map[0, 0] = 5
    region.terrain_ids[1, 1] = 2
    region.overlay_ids[2, 2] = 7
    region.collision_mask[3, 3] = True

    file_path = tmp_path / "region.npz"
    region.save(file_path)

    loaded = RegionArrays.load(file_path)
    assert loaded.height_map[0, 0] == 5
    assert loaded.terrain_ids[1, 1] == 2
    assert loaded.overlay_ids[2, 2] == 7
    assert loaded.collision_mask[3, 3]

