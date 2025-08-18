
from runepy.options_menu import KeyBindingManager


class FakeBase:
    def __init__(self):
        self.accepted: list[tuple[str, object]] = []
        self.ignored: list[str] = []

    def accept(self, evt: str, func):
        self.accepted.append((evt, func))

    def ignore(self, evt: str, func=None):
        self.ignored.append(evt)


def test_bind_and_rebind(monkeypatch):
    base = FakeBase()
    mgr = KeyBindingManager(base, {"action": "a"})

    called = []
    def press():
        called.append("press")
    def release():
        called.append("release")

    mgr.bind("action", press, release)
    assert ("a", press) in base.accepted
    assert ("a-up", release) in base.accepted

    mgr.rebind("action", "b")
    assert "a" in base.ignored and "a-up" in base.ignored
    assert ("b", press) in base.accepted
    assert ("b-up", release) in base.accepted
