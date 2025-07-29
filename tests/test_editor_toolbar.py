from runepy.editor_toolbar import EditorToolbar

class StubFrame:
    def __init__(self, **kw):
        self.kw = kw
        self.destroyed = False
    def destroy(self):
        self.destroyed = True

class StubMenu:
    def __init__(self, **kw):
        self.command = kw.get('command')
        self.kw = kw


def fake_create_ui(layout, manager=None, parent=None):
    frame = StubFrame()
    widgets = {'mode_menu': StubMenu(command=manager._set_mode)}
    return frame, widgets

class FakeEditor:
    def __init__(self):
        self.mode = 'tile'
        self.saved = False
        self.loaded = False
    def set_mode(self, mode):
        self.mode = mode
    def save_map(self):
        self.saved = True
    def load_map(self):
        self.loaded = True
    def open_texture_editor(self):
        pass

class FakeBase:
    pass


def test_toolbar_basic(monkeypatch):
    monkeypatch.setattr('runepy.editor_toolbar.create_ui', fake_create_ui)
    editor = FakeEditor()
    tb = EditorToolbar(FakeBase(), editor)
    tb._set_mode('Interactable')
    assert editor.mode == 'interactable'
