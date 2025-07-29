import importlib

modules = [
    'runepy.ui.editor.controller',
]
for m in modules:
    importlib.import_module(m)

class _FakeMouseWatcher:
    def hasMouse(self):
        return True
    def getMouse(self):
        return (0, 0)
    def is_button_down(self, btn):
        return False

class _FakeTaskMgr:
    def add(self, func, name):
        self.added = (func, name)
    def remove(self, name):
        self.removed = name

class _FakeBase:
    def __init__(self):
        self.mouseWatcherNode = _FakeMouseWatcher()
        self.taskMgr = _FakeTaskMgr()
        self.accepted = {}
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

class _FakeWidget:
    def __init__(self, pos=(0,0,0), frame=(-1,1,-1,1)):
        self._pos = list(pos)
        self._frame = frame
        self.children = []
    def getChildren(self):
        return self.children
    def getPos(self):
        return tuple(self._pos)
    def setPos(self, x,y,z):
        self._pos=[x,y,z]
    def __getitem__(self, k):
        if k=='frameSize':
            return self._frame
        raise KeyError(k)
    def getPythonTag(self, t):
        return t == 'debug_gui'

def test_editor_ignores_game_click(monkeypatch):
    from runepy.ui.editor import controller as ctr

    base = _FakeBase()
    monkeypatch.setattr(ctr, 'base', base)
    root = _FakeWidget()
    editor = ctr.UIEditorController(root)

    base.accept('mouse1', base.tile_click_event)
    # initial click works
    base.accepted['mouse1']()
    assert base.clicked == 1

    editor.enable()
    base.accepted['mouse1']()
    # game handler should not fire
    assert base.clicked == 1

    editor.disable()
    base.accepted['mouse1']()
    assert base.clicked == 2
