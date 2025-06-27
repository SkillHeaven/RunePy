from pathlib import Path
import json
from runepy.ui.debug_layout import LAYOUT as DEBUG_LAYOUT

from runepy.ui.manager import UIManager


def test_manager_load_and_toggle():
    mgr = UIManager()
    # layout from existing debug layout module
    mgr.load_ui("debug", "runepy.ui.debug_layout")
    assert "debug" in mgr.frames
    mgr.show_ui("debug")
    mgr.hide_ui("debug")
    mgr.destroy_ui("debug")


def test_manager_tags_and_json(tmp_path):
    mgr = UIManager()
    mgr.load_ui("debug", "runepy.ui.debug_layout")
    assert mgr.meta["debug"]["tags"] == ["debug"]
    mgr.destroy_ui("debug")

    json_path = Path(tmp_path / "sample.json")
    layout = dict(DEBUG_LAYOUT)
    layout["tags"] = ["temp"]
    json_path.write_text(json.dumps(layout))

    mgr.load_ui("temp", str(json_path))
    assert mgr.meta["temp"]["tags"] == ["temp"]
    mgr.destroy_ui("temp")
