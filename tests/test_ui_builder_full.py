from runepy.ui import builder

class FakeWidget:
    def __init__(self, **kw):
        self.kw = kw
    def __getitem__(self, k):
        return self.kw.get(k)
    def __setitem__(self, k, v):
        self.kw[k] = v

FakeFrame = FakeWidget
FakeButton = FakeWidget
FakeLabel = FakeWidget
FakeSlider = FakeWidget
FakeEntry = FakeWidget

class Manager:
    def __init__(self):
        self.clicked = False
        self.value = None
    def on_click(self):
        self.clicked = True
    def get_val(self):
        return 0.25
    def set_val(self, v):
        self.value = v


def test_build_all_widgets(monkeypatch):
    monkeypatch.setattr(builder, "DirectFrame", FakeFrame)
    monkeypatch.setattr(builder, "DirectButton", FakeButton)
    monkeypatch.setattr(builder, "DirectSlider", FakeSlider)
    monkeypatch.setattr(builder, "DirectLabel", FakeLabel)
    monkeypatch.setattr(builder, "DirectEntry", FakeEntry)
    builder._WIDGETS["entry"] = FakeEntry

    layout = {
        "type": "frame",
        "name": "root",
        "children": [
            {"type": "label", "name": "lbl", "text": "hi"},
            {"type": "button", "name": "btn", "command": "on_click"},
            {
                "type": "slider",
                "name": "sld",
                "getter": "get_val",
                "setter": "set_val",
                "range": [0, 1],
            },
            {"type": "entry", "name": "ent", "initialText": "abc"},
        ],
    }

    mgr = Manager()
    widgets = builder.build_ui(None, layout, mgr)
    assert set(widgets) == {"root", "lbl", "btn", "sld", "ent"}
    assert isinstance(widgets["ent"], FakeEntry)
    assert widgets["ent"].kw["initialText"] == "abc"

    widgets["btn"]["command"]()
    assert mgr.clicked

    widgets["sld"]["value"] = 0.5
    widgets["sld"]["command"]()
    assert mgr.value == 0.5
