"""GUI components for debugging.

This module wraps Panda3D's DirectGUI widgets. It can be imported safely even
when Panda3D is not available.
"""

from __future__ import annotations

try:
    from direct.gui.DirectGui import (
        DirectFrame,
        DirectButton,
        DirectSlider,
        DirectLabel,
    )
    from direct.task import Task
except Exception:  # pragma: no cover - Panda3D may be missing
    DirectFrame = object  # type: ignore
    DirectButton = object  # type: ignore
    DirectSlider = object  # type: ignore
    DirectLabel = object  # type: ignore
    Task = object  # type: ignore


class DebugWindow(DirectFrame):
    def __init__(self, mgr) -> None:
        super().__init__(
            frameColor=(0, 0, 0, 0.7),
            frameSize=(-0.6, 0.6, -0.4, 0.4),
            pos=(0.7, 0, 0.55),
        )
        self.mgr = mgr  # back-reference
        self._build_live_stats()
        self._build_actions()
        self._build_tweaks()
        self.hide()

    def _build_live_stats(self) -> None:
        self.stats_lbl = DirectLabel(text="", parent=self, pos=(-0.55, 0, 0.25), scale=0.05)

    def refresh_task(self, task: "Task"):
        from direct.showbase.ShowBaseGlobal import base, render
        world = getattr(base, "world", None)
        if world is not None:
            rm = world.region_manager
            regions = len(rm.loaded)
        else:
            regions = 0
        geoms = render.findAllMatches("**/+GeomNode").getNumPaths()
        self.stats_lbl["text"] = f"Regions: {regions:2d}\nGeoms:   {geoms:3d}"
        return task.again

    def _build_actions(self) -> None:
        y = 0.1
        DirectButton(text="Dump to console", command=self.mgr.dump_console, pos=(-0.45, 0, y), scale=0.05, parent=self)
        y -= 0.1
        DirectButton(text="Dump to file", command=self.mgr.dump_file, pos=(-0.45, 0, y), scale=0.05, parent=self)
        y -= 0.1
        DirectButton(text="Toggle PStats", command=self.mgr.toggle_pstats, pos=(-0.45, 0, y), scale=0.05, parent=self)
        y -= 0.1
        DirectButton(text="Reload region", command=self.mgr.reload_region, pos=(-0.45, 0, y), scale=0.05, parent=self)

    def _build_tweaks(self) -> None:
        try:
            from direct.showbase.ShowBaseGlobal import base
        except Exception:
            return

        def add_slider(y, text, min_, max_, getter, setter):
            DirectLabel(parent=self, text=text, pos=(-0.55, 0, y + 0.02), scale=0.05)
            try:
                value = getter()
                slider = DirectSlider(parent=self, range=(min_, max_), value=value, pos=(-0.05, 0, y), scale=0.4, command=lambda v: setter(float(v)))
            except Exception:
                slider = DirectSlider(parent=self, range=(min_, max_), value=min_, pos=(-0.05, 0, y), scale=0.4, state="disabled")
            return slider

        y = -0.15
        add_slider(y, "Avatar speed", 0.5, 10.0, lambda: base.player.walk_speed, lambda v: base.player.set_speed(v))
        y -= 0.1
        add_slider(y, "Cam pan-speed", 1.0, 40.0, lambda: base.camera_ctl.pan_speed, lambda v: base.camera_ctl.set_pan_speed(v))
        y -= 0.1
        add_slider(y, "Zoom step", 0.1, 5.0, lambda: base.camera_ctl.zoom_step, lambda v: base.camera_ctl.set_zoom_step(v))

    # ------------------------------------------------------------------
    def toggleVisible(self):
        if self.isHidden():
            self.show()
        else:
            self.hide()

__all__ = ["DebugWindow"]
