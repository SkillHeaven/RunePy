import types
from runepy.world.world import World
from runepy.texture_editor import TextureEditor

class _MultiBase:
    def __init__(self):
        self.accepted = {}
    def accept(self, evt, func):
        self.accepted.setdefault(evt, []).append(func)
    def ignore(self, evt, func=None):
        if func is None:
            self.accepted.pop(evt, None)
        else:
            handlers = self.accepted.get(evt)
            if handlers and func in handlers:
                handlers.remove(func)
                if not handlers:
                    self.accepted.pop(evt)
    def tile_click_event(self):
        self.clicked = getattr(self, 'clicked', 0) + 1
    def other_handler(self):
        self.other = getattr(self, 'other', 0) + 1


def test_other_handlers_removed(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    base = _MultiBase()
    world = World(view_radius=1)
    editor = TextureEditor(base, world)

    base.accept('mouse1', base.tile_click_event)
    base.accept('mouse1', base.other_handler)

    for f in list(base.accepted['mouse1']):
        f()
    assert base.clicked == 1 and base.other == 1

    base.clicked = 0
    base.other = 0

    editor.open(0, 0)
    assert 'mouse1' not in base.accepted
    if 'mouse1' in base.accepted:
        for f in list(base.accepted['mouse1']):
            f()
    assert base.clicked == 0
    assert base.other == 0

    editor.close()
    for f in list(base.accepted['mouse1']):
        f()
    assert base.clicked == 1
    assert base.other == 0
