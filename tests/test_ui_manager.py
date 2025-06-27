from runepy.ui.manager import UIManager


def test_manager_load_and_toggle():
    mgr = UIManager()
    # layout from existing debug layout module
    mgr.load_ui("debug", "runepy.ui.debug_layout")
    assert "debug" in mgr.frames
    mgr.show_ui("debug")
    mgr.hide_ui("debug")
    mgr.destroy_ui("debug")
