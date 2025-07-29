from runepy.editor_toolbar import EditorToolbar

class StubFrame:
    def __init__(self, **kw):
        self.kw = kw
        self.destroyed = False
    def destroy(self):
        self.destroyed = True

class StubMenu:
    def __init__(self, parent=None, items=None, command=None, **kw):
        self.items = items
        self.command = command
        self.kw = kw

class StubButton:
    def __init__(self, parent=None, text='', command=None, **kw):
        self.command = command
        self.kw = kw

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

class FakeBase:
    pass


def test_toolbar_basic(monkeypatch):
    monkeypatch.setattr('runepy.editor_toolbar.DirectFrame', StubFrame)
    monkeypatch.setattr('runepy.editor_toolbar.DirectOptionMenu', StubMenu)
    monkeypatch.setattr('runepy.editor_toolbar.DirectButton', StubButton)

    editor = FakeEditor()
    tb = EditorToolbar(FakeBase(), editor)
    tb._set_mode('Interactable')
    assert editor.mode == 'interactable'
