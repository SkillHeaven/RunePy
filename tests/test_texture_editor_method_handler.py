
from runepy.texture_editor import TextureEditor
from runepy.world.world import World


class _MethodBase:
    def __init__(self):
        self.accepted = {}
    def tile_click_event(self):
        self.clicked = getattr(self, 'clicked', 0) + 1
    def accept(self, evt, func):
        self.accepted[evt] = func
    def ignore(self, evt, func=None):
        if func is None:
            self.accepted.pop(evt, None)
        else:
            if evt in self.accepted and self.accepted[evt] is func:
                self.accepted.pop(evt)


def test_texture_editor_with_method_handler(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    base = _MethodBase()
    base.tile_click_event_ref = base.tile_click_event
    world = World(view_radius=1)
    editor = TextureEditor(base, world)

    base.accept('mouse1', base.tile_click_event_ref)
    base.accepted['mouse1']()
    assert base.clicked == 1

    editor.open(0, 0)
    if 'mouse1' in base.accepted:
        base.accepted['mouse1']()
    assert base.clicked == 1

    editor.close()
    base.accepted['mouse1']()
    assert base.clicked == 2
