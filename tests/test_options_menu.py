import types
from runepy.options_menu import OptionsMenu, KeyBindingManager

class FakeBase:
    def __init__(self):
        self.accepted: list[tuple[str, object]] = []
        self.ignored: list[str] = []

    def accept(self, evt: str, func):
        self.accepted.append((evt, func))

    def ignore(self, evt: str, func=None):
        self.ignored.append(evt)

class StubFrame:
    def __init__(self, **kw):
        self.kw = kw
        self.destroyed = False
    def destroy(self):
        self.destroyed = True

class StubEntry:
    def __init__(self, initialText="", **kw):
        self.text = initialText
    def get(self):
        return self.text


def fake_create_ui(layout, manager=None, parent=None):
    frame = StubFrame()
    widgets = {}
    def walk(node):
        name = node.get("name")
        typ = node.get("type")
        if typ == "entry":
            widgets[name] = StubEntry(node.get("initialText", ""))
        elif name:
            widgets[name] = object()
        for child in node.get("children", []):
            walk(child)
    walk(layout)
    return frame, widgets


def test_open_apply_close(monkeypatch):
    base = FakeBase()
    mgr = KeyBindingManager(base, {"jump": "space"})
    menu = OptionsMenu(base, mgr)

    monkeypatch.setattr("runepy.options_menu.create_ui", fake_create_ui)

    menu.open()
    assert menu.visible
    assert isinstance(menu.frame, StubFrame)
    assert "jump" in menu.entries

    menu.entries["jump"].text = "j"
    menu.apply()
    assert mgr.bindings["jump"] == "j"
    assert not menu.visible
    assert menu.frame is None
