from runepy.ui.builder import build_ui
from runepy.ui.debug_layout import LAYOUT


def test_build_ui_import():
    try:
        widgets = build_ui(None, LAYOUT)
    except ImportError:  # pragma: no cover - Panda3D missing
        widgets = build_ui(None, LAYOUT)
    expected = {
        'stats',
        'dump_console',
        'dump_file',
        'toggle_pstats',
        'reload_region',
        'avatar_speed',
        'cam_pan_speed',
        'zoom_step',
    }
    assert set(widgets.keys()) == expected

