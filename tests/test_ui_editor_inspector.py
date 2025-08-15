import importlib
import logging

from runepy.ui.editor import controller as ctr

# Ensure modules are loaded
importlib.import_module('runepy.ui.editor.gizmos')


class FakeEntry:
    def __init__(self, **kw):
        self.kw = kw
        self.text = ""
        self.cmd = None
        self.extra = None

    def enterText(self, text):
        self.text = text

    def set(self, text):
        self.text = text

    def __setitem__(self, key, value):
        if key == "command":
            self.cmd = value
        elif key == "extraArgs":
            self.extra = value
        else:
            self.kw[key] = value


class FakeFrame:
    def __init__(self, **kw):
        self.kw = kw
        self.bin = None

    def setBin(self, *args):
        self.bin = args


class FakeLabel:
    def __init__(self, **kw):
        self.kw = kw


class FakeGizmo:
    def __init__(self, target):
        self.target = target
        self.updated = False
        self.destroyed = False

    def update(self):
        self.updated = True

    def destroy(self):
        self.destroyed = True


class FakeTaskMgr:
    def add(self, func, name):
        self.added = (func, name)

    def remove(self, name):
        self.removed = name


class FakeMouseWatcher:
    def hasMouse(self):
        return False


class FakeBase:
    def __init__(self):
        self.mouseWatcherNode = FakeMouseWatcher()
        self.taskMgr = FakeTaskMgr()
        self.accepted = {}
        self.ignored = []

        def click():
            self.clicked = getattr(self, "clicked", 0) + 1
        self.tile_click_event = click

    def accept(self, evt, func):
        self.accepted[evt] = func

    def ignore(self, evt, func=None):
        self.ignored.append(evt)


class FakeWidget:
    def __init__(self, pos=(0, 0, 0), scale=1.0, frame=(-0.5, 0.5, -0.5, 0.5), color=(1, 1, 1, 1)):
        self._pos = list(pos)
        self._scale = scale
        self._frame = frame
        self._color = color
        self.children = []

    def getChildren(self):
        return self.children

    def getPos(self):
        return tuple(self._pos)

    def setPos(self, x, y, z):
        self._pos = [x, y, z]

    def getScale(self):
        return self._scale

    def setScale(self, s):
        self._scale = s

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


def setup_editor(monkeypatch):
    base = FakeBase()
    monkeypatch.setattr(ctr, "base", base)
    monkeypatch.setattr(ctr, "DirectFrame", FakeFrame)
    monkeypatch.setattr(ctr, "DirectLabel", FakeLabel)
    monkeypatch.setattr(ctr, "DirectEntry", FakeEntry)
    monkeypatch.setattr(ctr, "SelectionGizmo", FakeGizmo)

    root = FakeWidget(frame=(-1, 1, -1, 1))
    child = FakeWidget(pos=(0.2, 0, 0.3), scale=1.5)
    root.children.append(child)
    editor = ctr.UIEditorController(root)
    return editor, child


def test_inspector_updates_and_prop_changes(monkeypatch):
    editor, child = setup_editor(monkeypatch)

    editor.enable()

    # Inspector widgets created
    assert editor._inspector is not None
    assert isinstance(editor._inspector_x, FakeEntry)
    assert isinstance(editor._inspector_scale, FakeEntry)

    # Begin drag should update inspector fields
    editor._begin_drag(child, (0, 0))
    assert editor._inspector_x.text == "0.200"
    assert editor._inspector_scale.text == "1.500"

    # Changing properties via inspector callbacks
    editor._on_prop_change("0.5", "pos.x")
    assert child.getPos()[0] == 0.5

    editor._on_prop_change("2.0", "scale")
    assert child.getScale() == 2.0

    editor.disable()


def test_inspector_widgets_survive_failures(monkeypatch, caplog):
    class FailFrame(FakeFrame):
        def setBin(self, *args):
            raise RuntimeError("boom")

    base = FakeBase()
    monkeypatch.setattr(ctr, "base", base)
    monkeypatch.setattr(ctr, "DirectFrame", FailFrame)
    monkeypatch.setattr(ctr, "DirectLabel", FakeLabel)
    monkeypatch.setattr(ctr, "DirectEntry", FakeEntry)

    root = FakeWidget(frame=(-1, 1, -1, 1))
    editor = ctr.UIEditorController(root)
    caplog.set_level(logging.ERROR)

    editor.enable()

    assert isinstance(editor._inspector, FailFrame)
    assert isinstance(editor._inspector_x, FakeEntry)
    assert isinstance(editor._inspector_scale, FakeEntry)
    assert "Failed to set inspector bin" in caplog.text
