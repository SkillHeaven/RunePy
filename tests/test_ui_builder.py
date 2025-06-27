from runepy.ui.builder import build_ui
from runepy.ui.debug_layout import LAYOUT


def test_build_ui_import():
    try:
        widgets = build_ui(None, LAYOUT)
    except ImportError:  # pragma: no cover - Panda3D missing
        widgets = build_ui(None, LAYOUT)
    assert widgets == {}

