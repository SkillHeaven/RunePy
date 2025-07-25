import types
from runepy.options_menu import OptionsMenu, KeyBindingManager

class FakeBase:
    def __init__(self):
        self.accepted: list[tuple[str, object]] = []
        self.ignored: list[str] = []

    def accept(self, evt: str, func):
        self.accepted.append((evt, func))

    def ignore(self, evt: str):
        self.ignored.append(evt)


class StubFrame:
    def __init__(self, **kw):
        self.kw = kw
        self.destroyed = False

    def destroy(self):
        self.destroyed = True


class StubLabel:
    def __init__(self, **kw):
        pass


class StubEntry:
    def __init__(self, initialText='', **kw):
        self.text = initialText

    def get(self):
        return self.text


class StubButton:
    def __init__(self, text='', command=None, **kw):
        self.command = command


def test_open_apply_close(monkeypatch):
    base = FakeBase()
    mgr = KeyBindingManager(base, {"jump": "space"})
    menu = OptionsMenu(base, mgr)

    monkeypatch.setattr("runepy.options_menu.DirectFrame", StubFrame)
    monkeypatch.setattr("runepy.options_menu.DirectLabel", StubLabel)
    monkeypatch.setattr("runepy.options_menu.DirectEntry", StubEntry)
    monkeypatch.setattr("runepy.options_menu.DirectButton", StubButton)

    menu.open()
    assert menu.visible
    assert isinstance(menu.frame, StubFrame)
    assert "jump" in menu.entries

    menu.entries["jump"].text = "j"
    menu.apply()
    assert mgr.bindings["jump"] == "j"
    assert not menu.visible
    assert menu.frame is None
