import types

from panda3d.core import NodePath

from runepy.texture_editor import TextureEditor


class _FakeBase:
    def __init__(self):
        self.accepted = {}
        self.render = NodePath('render')
        self.camera = NodePath('camera')
        self.taskMgr = types.SimpleNamespace(add=lambda *a, **k: None)
        self.mouseWatcherNode = None
        def click():
            self.clicked = getattr(self, 'clicked', 0) + 1
        self.tile_click_event = click
    def accept(self, evt, func):
        self.accepted[evt] = func
    def ignore(self, evt, func=None):
        if func is None:
            self.accepted.pop(evt, None)
        else:
            if evt in self.accepted and self.accepted[evt] is func:
                self.accepted.pop(evt)
    def disableMouse(self):
        pass
    def setBackgroundColor(self, *a, **k):
        pass

class _FakeMapEditor:
    def __init__(self, client, world):
        self.client = client
        self.world = world
        self.texture_editor = TextureEditor(client, world)
    def register_bindings(self, mgr):
        pass
    def handle_click(self):
        self.client.clicked = getattr(self.client, 'clicked', 0) + 1

class _FakeCamera:
    def __init__(self, *a, **k):
        pass
    def start(self, base):
        pass
    def set_move(self, *a, **k):
        pass

class _FakeControls:
    def __init__(self, *a, **k):
        pass

class _FakeKeyManager:
    def __init__(self, *a, **k):
        pass
    def bind(self, *a, **k):
        pass

class _FakeOptionsMenu:
    def __init__(self, *a, **k):
        self.visible = False
    def toggle(self):
        self.visible = not self.visible

class _FakeToolbar:
    def __init__(self, *a, **k):
        pass


def test_editor_window_texture_click_override(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("runepy.base_app.BaseApp", _FakeBase)
    monkeypatch.setattr('runepy.editor_window.BaseApp', _FakeBase)
    monkeypatch.setattr('runepy.editor_window.MapEditor', _FakeMapEditor)
    monkeypatch.setattr('runepy.editor_window.FreeCameraControl', _FakeCamera)
    monkeypatch.setattr('runepy.editor_window.Controls', _FakeControls)
    monkeypatch.setattr('runepy.editor_window.KeyBindingManager', _FakeKeyManager)
    monkeypatch.setattr('runepy.editor_window.OptionsMenu', _FakeOptionsMenu)
    monkeypatch.setattr('runepy.editor_window.EditorToolbar', _FakeToolbar)

    from runepy.editor_window import EditorWindow

    app = EditorWindow()
    app.initialize()

    app.accepted['mouse1']()
    assert app.clicked == 1

    app.editor.texture_editor.open(0, 0)
    if 'mouse1' in app.accepted:
        app.accepted['mouse1']()
    assert app.clicked == 1

    app.editor.texture_editor.close()
    app.accepted['mouse1']()
    assert app.clicked == 2
