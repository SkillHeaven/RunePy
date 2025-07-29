import importlib
from pathlib import Path

from runepy.ui.editor import controller as ctr

class FakeWidget:
    def __init__(self, pos=(0,0,0), frame=(-0.5,0.5,-0.5,0.5)):
        self._pos = list(pos)
        self._frame = frame
    def getPos(self):
        return tuple(self._pos)
    def setPos(self, x, y, z):
        self._pos = [x,y,z]
    def __getitem__(self, k):
        if k == "frameSize":
            return self._frame
        raise KeyError(k)
    def getPythonTag(self, tag):
        return tag == "debug_gui"
    def getChildren(self):
        return []

class FakeGizmo:
    def __init__(self, target):
        self.target = target
        self.updated = False
    def update(self):
        self.updated = True
    def destroy(self):
        self.destroyed = True

class FakeBase:
    def __init__(self):
        class _MW:
            def hasMouse(self):
                return False
        self.mouseWatcherNode = _MW()
        class _TM:
            def remove(self, name):
                self.removed = name
        self.taskMgr = _TM()


def test_nudge(monkeypatch):
    monkeypatch.setattr(ctr, "base", FakeBase())
    w = FakeWidget()
    editor = ctr.UIEditorController(FakeWidget())
    editor._gizmo = FakeGizmo(w)
    w.setPos(0,0,0)
    editor._gizmo.target = w
    editor._nudge(0.1, 0.2)
    assert w.getPos() == (0.1,0,0.2)
    assert editor._gizmo.updated


def test_save(monkeypatch, tmp_path):
    saved = {}
    def fake_dump(root, path):
        saved['path'] = Path(path)
    monkeypatch.setattr(ctr, "dump_layout", fake_dump)
    monkeypatch.setattr(ctr, "base", FakeBase())
    editor = ctr.UIEditorController(FakeWidget())
    out_path = tmp_path / "layout.json"
    editor._save(out_path)
    assert saved['path'] == out_path


def test_enable_disable(monkeypatch):
    class _MW:
        def hasMouse(self):
            return False

    class _TM:
        def __init__(self):
            self.added = None
            self.removed = None
        def add(self, func, name):
            self.added = name
        def remove(self, name):
            self.removed = name

    class _Base:
        def __init__(self):
            self.mouseWatcherNode = _MW()
            self.taskMgr = _TM()
            self.accepted = {}
        def accept(self, evt, func):
            self.accepted[evt] = func
        def ignore(self, evt, func=None):
            if func is None:
                self.accepted.pop(evt, None)
            else:
                if evt in self.accepted and self.accepted[evt] is func:
                    self.accepted.pop(evt)

    class _Widget:
        def __init__(self, color=(1,1,1,1)):
            self._pos = [0,0,0]
            self._frame = (-0.5,0.5,-0.5,0.5)
            self._color = color
        def getChildren(self):
            return []
        def getPos(self):
            return tuple(self._pos)
        def setPos(self, x, y, z):
            self._pos = [x,y,z]
        def __getitem__(self, key):
            if key == "frameSize":
                return self._frame
            if key == "frameColor":
                return self._color
            raise KeyError(key)
        def __setitem__(self, key, value):
            if key == "frameColor":
                self._color = value
            else:
                raise KeyError(key)
        def getPythonTag(self, tag):
            return tag == "debug_gui"

    base = _Base()
    monkeypatch.setattr(ctr, "base", base)
    root = _Widget()
    editor = ctr.UIEditorController(root)

    original_color = root["frameColor"]
    editor.enable()
    assert base.taskMgr.added == "ui-editor-move"

    gizmo = FakeGizmo(root)
    editor._gizmo = gizmo

    editor.disable()
    assert gizmo.destroyed
    assert editor._gizmo is None
    assert root["frameColor"] == original_color
    assert base.taskMgr.removed == "ui-editor-move"


def test_enable_disable_drag_task(monkeypatch):
    class _MW:
        def hasMouse(self):
            return False

    class _TM:
        def __init__(self):
            self.tasks: list[str] = []
        def add(self, func, name):  # pragma: no cover - stub
            self.tasks.append(name)
        def remove(self, name):  # pragma: no cover - stub
            if name in self.tasks:
                self.tasks.remove(name)

    class _Base:
        def __init__(self):
            self.mouseWatcherNode = _MW()
            self.taskMgr = _TM()
            self.accepted = {}
        def accept(self, evt, func):
            self.accepted[evt] = func
        def ignore(self, evt, func=None):
            if func is None:
                self.accepted.pop(evt, None)
            else:
                if evt in self.accepted and self.accepted[evt] is func:
                    self.accepted.pop(evt)

    class _Widget:
        def __init__(self, color=(1,1,1,1)):
            self._pos = [0,0,0]
            self._frame = (-0.5,0.5,-0.5,0.5)
            self._color = color
        def getChildren(self):
            return []
        def __getitem__(self, key):
            if key == "frameSize":
                return self._frame
            if key == "frameColor":
                return self._color
            raise KeyError(key)
        def __setitem__(self, key, value):
            if key == "frameColor":
                self._color = value
            else:
                raise KeyError(key)
        def getPythonTag(self, tag):
            return tag == "debug_gui"

    base = _Base()
    monkeypatch.setattr(ctr, "base", base)
    root = _Widget()
    editor = ctr.UIEditorController(root)

    orig_color = root["frameColor"]
    editor.enable()
    # ensure move task added
    assert "ui-editor-move" in base.taskMgr.tasks

    gizmo = FakeGizmo(root)
    editor._gizmo = gizmo

    editor.disable()
    assert gizmo.destroyed
    assert editor._gizmo is None
    assert root["frameColor"] == orig_color
    assert "ui-editor-move" not in base.taskMgr.tasks
    assert "ui-editor-drag" not in base.taskMgr.tasks
