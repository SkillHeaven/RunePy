from constants import REGION_SIZE
from runepy.world import World


def test_streaming_consistency(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    w = World(view_radius=1)
    for i in range(10):
        x = (i + 1) * REGION_SIZE
        w.update_streaming(x, 0)
        assert len(w.manager.loaded) <= 9
    w.update_streaming(0, 0)
    assert len(w.manager.loaded) <= 9
