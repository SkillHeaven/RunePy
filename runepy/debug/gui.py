"""GUI components for debugging."""
from __future__ import annotations

try:
    from direct.gui.DirectGui import DirectFrame
    from direct.task import Task
except Exception:  # pragma: no cover - Panda3D may be missing
    DirectFrame = object  # type: ignore
    Task = object  # type: ignore

from runepy.ui.builder import build_ui
from runepy.ui.debug_layout import LAYOUT as L


class DebugWindow(DirectFrame):
    def __init__(self, manager) -> None:
        super().__init__()
        self.widgets = build_ui(self, L, manager)
        # Keep children clipped inside the window frame
        if hasattr(self, "setClipFrame") and "frameSize" in self:
            try:
                self.setClipFrame(self["frameSize"])
            except Exception:
                pass
        self.hide()

    # ------------------------------------------------------------------
    def toggleVisible(self):
        if self.isHidden():
            self.show()
        else:
            self.hide()

    def refresh_task(self, task: "Task"):
        if "stats" not in self.widgets:
            return task.again
        try:
            from direct.showbase.ShowBaseGlobal import base, render
        except Exception:
            return task.again
        world = getattr(base, "world", None)
        if world is not None:
            rm = world.region_manager
            regions = len(rm.loaded)
        else:
            regions = 0
        geoms = render.findAllMatches("**/+GeomNode").getNumPaths()
        self.widgets["stats"]["text"] = f"Regions: {regions:2d}\nGeoms:   {geoms:3d}"
        return task.again


__all__ = ["DebugWindow"]
