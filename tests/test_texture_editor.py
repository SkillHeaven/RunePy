import types

from runepy.map_editor import MapEditor
from runepy.world.world import World


class StubFrame:
    def __init__(self, **kw):
        self.kw = kw
    def hide(self):
        self.hidden = True
    def show(self):
        self.hidden = False

class StubButton:
    def __init__(self, **kw):
        self.command = kw.get('command')
    def __setitem__(self, key, val):
        pass


def fake_create_ui(layout, manager=None, parent=None):
    frame = StubFrame()
    widgets = {}
    def walk(node):
        name = node.get('name')
        typ = node.get('type')
        if typ == 'button':
            widgets[name] = StubButton()
        elif name:
            widgets[name] = object()
        for child in node.get('children', []):
            walk(child)
    walk(layout)
    return frame, widgets

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
    monkeypatch.setattr('runepy.texture_editor.create_ui', fake_create_ui)
    world = World(view_radius=1)
    client = _FakeClient()
    editor = MapEditor(client, world)
    monkeypatch.setattr('runepy.map_editor.get_tile_from_mouse', lambda *a: (0,0))

    editor.open_texture_editor()
    editor.texture_editor.set_color(123)
    editor.texture_editor.paint(5, 6)
    region = world.region_manager.loaded[(0,0)]
    assert region.textures[0, 0, 6, 5] == 123
