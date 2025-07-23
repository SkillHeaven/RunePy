import types
import importlib

modules = [
    'runepy.map_editor',
]
for mod in modules:
    importlib.import_module(mod)

from runepy.map_editor import MapEditor
from runepy.world import World
from runepy.terrain import FLAG_BLOCKED


class _FakeClient:
    def __init__(self):
        from panda3d.core import NodePath
        self.options_menu = types.SimpleNamespace(visible=False)
        self.mouseWatcherNode = None
        self.camera = None
        self.render = NodePath('render')
        self.tile_root = NodePath('tile_root')


def test_toggle_tile_and_interactable(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    world = World(view_radius=1)
    client = _FakeClient()
    editor = MapEditor(client, world)

    monkeypatch.setattr('runepy.map_editor.get_tile_from_mouse',
                        lambda mw, cam, ren: (2, 3))

    editor.toggle_tile()
    region = world.region_manager.loaded[(0, 0)]
    assert region.flags[3, 2] & FLAG_BLOCKED

    monkeypatch.setattr('runepy.map_editor.get_tile_from_mouse',
                        lambda mw, cam, ren: (5, 6))
    editor.toggle_interactable()
    assert region.overlay[6, 5] == 1


def test_save_and_load_map(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    world = World(view_radius=1)
    client = _FakeClient()
    editor = MapEditor(client, world)
    world.region_manager.ensure(0, 0)
    region = world.region_manager.loaded[(0, 0)]

    region.overlay[1, 1] = 1
    editor.save_map()
    map_file = tmp_path / 'maps' / 'region_0_0.bin'
    assert map_file.exists()

    region.overlay[1, 1] = 0
    editor.load_map()
    loaded = world.region_manager.loaded[(0, 0)]
    assert loaded.overlay[1, 1] == 1
