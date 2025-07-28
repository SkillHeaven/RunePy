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
