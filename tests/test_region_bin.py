import gzip

import numpy as np

from constants import REGION_SIZE
from runepy.paths import MAPS_DIR
from runepy.world.region import Region


def test_region_round_trip(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    r1 = Region.load(0, 0)
    assert r1.height.shape == (REGION_SIZE, REGION_SIZE)
    r1.height[1, 1] = 5
    r1.base[2, 2] = 3
    r1.overlay[3, 3] = 4
    r1.flags[4, 4] = 7
    r1.textures[5, 5, 0, 0] = 255
    r1.save()

    r2 = Region.load(0, 0)
    assert np.array_equal(r1.height, r2.height)
    assert np.array_equal(r1.base, r2.base)
    assert np.array_equal(r1.overlay, r2.overlay)
    assert np.array_equal(r1.flags, r2.flags)
    assert np.array_equal(r1.textures, r2.textures)


def test_region_load_v1(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    path = MAPS_DIR / "region_0_0.bin"
    path.parent.mkdir(parents=True)

    size = REGION_SIZE * REGION_SIZE
    height = np.zeros((REGION_SIZE, REGION_SIZE), dtype=np.int16)
    base = np.zeros((REGION_SIZE, REGION_SIZE), dtype=np.uint8)
    overlay = np.zeros((REGION_SIZE, REGION_SIZE), dtype=np.uint8)
    flags = np.zeros((REGION_SIZE, REGION_SIZE), dtype=np.uint8)
    height[1, 1] = 1
    with gzip.open(path, "wb") as f:
        f.write((1).to_bytes(2, "little"))
        f.write(height.tobytes())
        f.write(base.tobytes())
        f.write(overlay.tobytes())
        f.write(flags.tobytes())

    loaded = Region.load(0, 0)
    assert loaded.height[1, 1] == 1
    assert loaded.textures.shape == (REGION_SIZE, REGION_SIZE, 16, 16)
    assert np.all(loaded.textures == 0)
