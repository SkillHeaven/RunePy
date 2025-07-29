class FakeBase:
    def __init__(self):
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

class StubFrame:
    def __init__(self, *a, **k):
        self.hidden = True
    def show(self):
        self.hidden = False
    def hide(self):
        self.hidden = True
    def isHidden(self):
        return self.hidden
    def setClipFrame(self, *a, **k):
        pass

def test_debug_window_click_override(monkeypatch):
    import runepy.debug.gui as gui
    from runepy.debug import get_debug

    monkeypatch.setattr(gui, 'DirectFrame', StubFrame)
    monkeypatch.setattr(gui, 'build_ui', lambda *a, **k: {})

    dbg = get_debug()
    base = FakeBase()
    dbg.attach(base)

    base.accept('mouse1', base.tile_click_event)
    base.accepted['mouse1']()
    assert base.clicked == 1

    dbg.window.toggleVisible()
    if 'mouse1' in base.accepted:
        base.accepted['mouse1']()
    assert base.clicked == 1

    dbg.window.toggleVisible()
    base.accepted['mouse1']()
    assert base.clicked == 2
