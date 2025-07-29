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
        self.manager = manager
        self.widgets = build_ui(self, L, manager)
        self._orig_click_handler = None
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
            self._suspend_click()
        else:
            self.hide()
            self._restore_click()

    def _suspend_click(self) -> None:
        base = getattr(self.manager, "base", None)
        handler = None
        if base is not None:
            handler = getattr(base, "tile_click_event_ref", None)
            if handler is None:
                handler = getattr(base, "tile_click_event", None)
            if handler is not None:
                try:
                    base.ignore("mouse1", handler)
                except Exception:
                    handler = None
        self._orig_click_handler = handler

    def _restore_click(self) -> None:
        base = getattr(self.manager, "base", None)
        handler = self._orig_click_handler
        if base is not None and handler is not None:
            try:
                base.accept("mouse1", handler)
            except Exception:
                pass
        self._orig_click_handler = None

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
        self.widgets["stats"]["text"] = (
            f"Regions: {regions:2d}\nGeoms:   {geoms:3d}"
        )
        return task.again


__all__ = ["DebugWindow"]
