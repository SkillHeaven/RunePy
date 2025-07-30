import importlib.util
from pathlib import Path

_stubs_spec = importlib.util.spec_from_file_location(
    "stubs", Path(__file__).parent / "test_editor_window_method_handler.py"
)
_stubs = importlib.util.module_from_spec(_stubs_spec)
assert _stubs_spec and _stubs_spec.loader
_stubs_spec.loader.exec_module(_stubs)

_MethodBase = _stubs._MethodBase
_FakeMapEditor = _stubs._FakeMapEditor
_FakeCamera = _stubs._FakeCamera
_FakeControls = _stubs._FakeControls
_FakeKeyManager = _stubs._FakeKeyManager
_FakeOptionsMenu = _stubs._FakeOptionsMenu
_FakeToolbar = _stubs._FakeToolbar

class FakeUIEditor:
    def __init__(self, parent):
        self.parent = parent
        self.enabled = False
        self.enabled_calls = 0
        self.disabled_calls = 0
    def enable(self):
        self.enabled = True
        self.enabled_calls += 1
    def disable(self):
        self.enabled = False
        self.disabled_calls += 1

class StoreKeyManager(_FakeKeyManager):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.bindings = {}
    def bind(self, name, on_press, on_release=None):
        self.bindings[name] = on_press

class ToolbarWithFrame(_FakeToolbar):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.frame = object()


def test_ui_editor_toggle(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("runepy.base_app.BaseApp", _MethodBase)
    monkeypatch.setattr("runepy.editor_window.BaseApp", _MethodBase)
    monkeypatch.setattr("runepy.editor_window.MapEditor", _FakeMapEditor)
    monkeypatch.setattr("runepy.editor_window.FreeCameraControl", _FakeCamera)
    monkeypatch.setattr("runepy.editor_window.Controls", _FakeControls)
    monkeypatch.setattr("runepy.editor_window.KeyBindingManager", StoreKeyManager)
    monkeypatch.setattr("runepy.editor_window.OptionsMenu", _FakeOptionsMenu)
    monkeypatch.setattr("runepy.editor_window.EditorToolbar", ToolbarWithFrame)
    monkeypatch.setattr("runepy.editor_window.UIEditorController", FakeUIEditor)

    from runepy.editor_window import EditorWindow

    app = EditorWindow()
    app.initialize()

    assert isinstance(app.ui_editor, FakeUIEditor)
    km = app.key_manager
    assert "toggle_ui_editor" in km.bindings
    toggle = km.bindings["toggle_ui_editor"]
    toggle()
    assert app.ui_editor.enabled
    toggle()
    assert not app.ui_editor.enabled
