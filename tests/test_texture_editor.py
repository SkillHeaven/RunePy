import types
from runepy.world import World
from runepy.map_editor import MapEditor

class StubFrame:
    def __init__(self, **kw):
        self.kw = kw
    def hide(self):
        self.hidden = True
    def show(self):
        self.hidden = False

class StubButton:
    def __init__(self, parent=None, text="", scale=0.0, pos=(0,0,0), command=None, **kw):
        self.command = command
    def __setitem__(self, key, val):
        pass

class _FakeClient:
    def __init__(self):
        from panda3d.core import NodePath
        self.options_menu = types.SimpleNamespace(visible=False)
        self.mouseWatcherNode = None
        self.camera = None
        self.render = NodePath('render')
        self.tile_root = NodePath('tile_root')


def test_texture_paint(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr('runepy.texture_editor.DirectFrame', StubFrame)
    monkeypatch.setattr('runepy.texture_editor.DirectButton', StubButton)
    world = World(view_radius=1)
    client = _FakeClient()
    editor = MapEditor(client, world)
    monkeypatch.setattr('runepy.map_editor.get_tile_from_mouse', lambda *a: (0, 0))

    editor.open_texture_editor()
    editor.texture_editor.set_color(123)
    editor.texture_editor.paint(5, 6)
    region = world.region_manager.loaded[(0,0)]
    assert region.textures[0, 0, 6, 5] == 123
