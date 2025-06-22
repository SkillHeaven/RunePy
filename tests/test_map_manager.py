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
