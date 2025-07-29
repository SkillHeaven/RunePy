import numpy as np
from constants import REGION_SIZE
from runepy.world.world import World
from runepy.terrain import FLAG_BLOCKED


def test_update_streaming_calls_ensure(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    w = World(view_radius=1)

    calls = []
    real_ensure = w.manager.ensure

    def mock_ensure(x, y):
        calls.append((x, y))
        real_ensure(x, y)

    monkeypatch.setattr(w.manager, "ensure", mock_ensure)

    w.update_streaming(10, 10)  # first call
    w.update_streaming(20, 20)  # same region
    assert len(calls) == 1

    w.update_streaming(REGION_SIZE + 5, 10)  # different region
    assert len(calls) == 2


def test_world_streaming_region_limit(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    w = World(view_radius=1)
    for x in range(0, REGION_SIZE * 4, REGION_SIZE):
        for y in range(0, REGION_SIZE * 4, REGION_SIZE):
            w.update_streaming(x, y)
            assert len(w.manager.loaded) <= 9


def test_is_walkable(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    w = World(view_radius=1)
    w.update_streaming(0, 0)
    region = w.manager.loaded[(0, 0)]
    region.flags[1, 1] = FLAG_BLOCKED
    assert not w.is_walkable(1, 1)
    assert w.is_walkable(2, 2)
