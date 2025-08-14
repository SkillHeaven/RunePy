from runepy.map_manager import MapManager


def test_region_loading(tmp_path, monkeypatch):
    # Ensure new regions are saved to tmp directory
    monkeypatch.chdir(tmp_path)
    manager = MapManager(region_size=64, view_distance=1)
    manager.update(10, 10)
    assert len(manager.loaded) == 9  # 3x3 block

    manager.update(70, 10)  # move one region east
    assert (1, 0) in manager.loaded
    assert (0, 0) in manager.loaded
    # Should still keep 9 regions loaded
    assert len(manager.loaded) == 9
    # Regions far west should have been unloaded
    assert (-1, 0) not in manager.loaded



def test_update_loads_and_unloads_regions(monkeypatch):
    manager = MapManager(region_size=64, view_distance=0)
    load_calls = []
    unload_calls = []

    def fake_load_region(rx, ry):
        load_calls.append((rx, ry))
        return f"region-{rx}-{ry}"

    def fake_unload_region(rx, ry):
        unload_calls.append((rx, ry))
        manager.loaded.pop((rx, ry), None)

    monkeypatch.setattr(manager, 'load_region', fake_load_region)
    monkeypatch.setattr(manager, 'unload_region', fake_unload_region)

    manager.update(63, 63)
    assert load_calls == [(0, 0)]
    assert (0, 0) in manager.loaded

    manager.update(64, 63)
    assert load_calls[-1] == (1, 0)
    assert unload_calls == [(0, 0)]
    assert (1, 0) in manager.loaded
    assert (0, 0) not in manager.loaded


def test_region_id_edges_and_uniqueness():
    manager = MapManager()
    origin = manager.region_id(0, 0)
    edge = manager.region_id(255, 255)
    large1 = manager.region_id(1024, 1024)
    large2 = manager.region_id(1024, 1025)

    assert origin == 0
    assert edge == 0xFFFF
    assert len({origin, edge, large1, large2}) == 4
    assert all(isinstance(i, int) for i in (origin, edge, large1, large2))
