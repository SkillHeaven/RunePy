import importlib

modules = [
    'runepy.ui.editor.controller',
    'runepy.ui.editor.gizmos',
    'runepy.ui.editor.serializer',
]

for mod in modules:
    importlib.import_module(mod)


class _FakeMouseWatcher:
    def __init__(self) -> None:
        self.pos = (0, 0)

    def hasMouse(self) -> bool:
        return True

    def getMouse(self):
        return self.pos

    def is_button_down(self, btn: str) -> bool:  # pragma: no cover - stub
        return False


class _FakeTaskMgr:
    def add(self, func, name):  # pragma: no cover - stub
        self.added = (func, name)

    def remove(self, name):  # pragma: no cover - stub
        self.removed = name


class _FakeBase:
    def __init__(self) -> None:
        self.mouseWatcherNode = _FakeMouseWatcher()
        self.taskMgr = _FakeTaskMgr()
        self.accepted: dict[str, callable] = {}
        self.ignored: list[str] = []

    def accept(self, evt: str, func):  # pragma: no cover - stub
        self.accepted[evt] = func

    def ignore(self, evt: str):  # pragma: no cover - stub
        self.ignored.append(evt)


class _FakeWidget:
    def __init__(self, pos=(0, 0, 0), frame=(-0.5, 0.5, -0.5, 0.5)) -> None:
        self._pos = list(pos)
        self._frame = frame
        self.children: list[_FakeWidget] = []

    def getChildren(self):  # pragma: no cover - stub
        return self.children

    def getPos(self):  # pragma: no cover - stub
        return tuple(self._pos)

    def setPos(self, x, y, z):  # pragma: no cover - stub
        self._pos = [x, y, z]

    def __getitem__(self, key):  # pragma: no cover - stub
        if key == "frameSize":
            return self._frame
        raise KeyError(key)

    def getPythonTag(self, tag):  # pragma: no cover - stub
        return tag == "debug_gui"


def test_begin_and_finish_drag(monkeypatch):
    from runepy.ui.editor import controller as ctr

    fake_base = _FakeBase()
    monkeypatch.setattr(ctr, "base", fake_base)

    root = _FakeWidget(pos=(0, 0, 0), frame=(-1, 1, -1, 1))
    child = _FakeWidget(pos=(0, 0, 0), frame=(-0.2, 0.2, -0.2, 0.2))
    root.children.append(child)

    editor = ctr.UIEditorController(root)
    began: list[object] = []
    ended: list[object] = []

    def _begin(w, m):
        began.append(w)

    def _end():
        ended.append(True)

    editor._begin_drag = _begin  # type: ignore[assignment]
    editor._finish_drag = _end  # type: ignore[assignment]

    editor.enable()
    fake_base.mouseWatcherNode.pos = (0, 0)
    fake_base.accepted["mouse1"]()
    assert began and began[0] is child
    fake_base.accepted["mouse1-up"]()
    assert ended
    editor.disable()


def test_mouse_down_with_offset_root(monkeypatch):
    from runepy.ui.editor import controller as ctr

    fake_base = _FakeBase()
    monkeypatch.setattr(ctr, "base", fake_base)

    root = _FakeWidget(pos=(0.7, 0, 0.55), frame=(-1, 1, -1, 1))
    child = _FakeWidget(pos=(0, 0, 0), frame=(-0.2, 0.2, -0.2, 0.2))
    root.children.append(child)

    editor = ctr.UIEditorController(root)
    began: list[object] = []

    def _begin(w, m):
        began.append(w)

    editor._begin_drag = _begin  # type: ignore[assignment]

    editor.enable()
    fake_base.mouseWatcherNode.pos = (0.7, 0.55)
    fake_base.accepted["mouse1"]()
    assert began and began[0] is child
    editor.disable()
