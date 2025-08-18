import numpy as np

from runepy.array_map import RegionArrays


def test_empty_arrays_zeroed_and_dtypes():
    region = RegionArrays.empty(shape=(8, 8))

    assert region.height_map.shape == (8, 8)
    assert region.terrain_ids.shape == (8, 8)
    assert region.overlay_ids.shape == (8, 8)
    assert region.collision_mask.shape == (8, 8)

    assert np.count_nonzero(region.height_map) == 0
    assert region.height_map.dtype == np.int16

    assert np.count_nonzero(region.terrain_ids) == 0
    assert region.terrain_ids.dtype == np.uint8

    assert np.count_nonzero(region.overlay_ids) == 0
    assert region.overlay_ids.dtype == np.uint8

    assert np.count_nonzero(region.collision_mask) == 0
    assert region.collision_mask.dtype == bool


def test_save_and_load_roundtrip(tmp_path):
    region = RegionArrays.empty(shape=(8, 8))
    region.height_map[:] = np.arange(64, dtype=np.int16).reshape(8, 8)
    region.terrain_ids[:] = np.arange(64, dtype=np.uint8).reshape(8, 8)
    region.overlay_ids[:] = np.full((8, 8), 7, dtype=np.uint8)
    region.collision_mask[:] = np.eye(8, dtype=bool)

    file_path = tmp_path / "region.npz"
    region.save(file_path)

    loaded = RegionArrays.load(file_path)
    assert np.array_equal(loaded.height_map, region.height_map)
    assert np.array_equal(loaded.terrain_ids, region.terrain_ids)
    assert np.array_equal(loaded.overlay_ids, region.overlay_ids)
    assert np.array_equal(loaded.collision_mask, region.collision_mask)
