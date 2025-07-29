import types
from runepy.world import World
from runepy.texture_editor import TextureEditor

class _FakeBase:
    def __init__(self):
        self.accepted = {}
    def accept(self, evt, func):
        self.accepted[evt] = func
    def ignore(self, evt):
        self.accepted.pop(evt, None)
    def tile_click_event(self):
        self.clicked = getattr(self, 'clicked', 0) + 1


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
