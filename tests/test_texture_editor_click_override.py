
from runepy.texture_editor import TextureEditor
from runepy.world.world import World


class _FakeBase:
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


def test_texture_editor_ignores_game_click(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    base = _FakeBase()
    world = World(view_radius=1)
    editor = TextureEditor(base, world)

    base.accept('mouse1', base.tile_click_event)
    base.accepted['mouse1']()
    assert base.clicked == 1

    editor.open(0, 0)
    if 'mouse1' in base.accepted:
        base.accepted['mouse1']()
    assert base.clicked == 1

    editor.close()
    base.accepted['mouse1']()
    assert base.clicked == 2
