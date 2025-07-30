"""Debug utilities for RunePy.

This module exposes a :class:`DebugManager` singleton via :func:`get_debug`.
Importing the package will not raise ImportError even if Panda3D's ``direct``
module is unavailable.
"""

from __future__ import annotations
from runepy.logging_config import LOG_DIR
import logging
logger = logging.getLogger(__name__)
from pathlib import Path
import datetime

from typing import Optional, Any


class NullDebugManager:
    """Fallback manager used when Panda3D is unavailable."""

    def __init__(self) -> None:
        self.window = None
        self.base = None

    def attach(self, base: Any | None = None) -> None:
        self.base = base

    def enable(self) -> None:
        pass

    def toggle(self) -> None:
        pass

    def dump_console(self) -> None:
        pass

    def dump_file(self) -> None:
        pass

    def toggle_pstats(self) -> None:
        pass

    def reload_region(self) -> None:
        pass


class DebugManager:
    """Simple container for debug helpers."""

    def __init__(self) -> None:
        self.log_file: Optional[Path] = None
        self.window = None
        self.base = None
        self._drag_start = None
        self._orig_pos = None

    def enable(self) -> None:
        if self.window is None or self.base is None:
            return
        try:
            self.base.taskMgr.doMethodLater(0.5, self.window.refresh_task, "dbg-refresh")
        except Exception:
            pass

    def toggle(self) -> None:
        """Toggle visibility of the debug window if available."""
        if self.window is None:
            return
        if self.window.isHidden():
            self.window.show()
        else:
            self.window.hide()
    def _start_drag(self, _evt: Any | None = None) -> None:
        if self.window is None or self.base is None:
            return
        base = self.base
        if not base.mouseWatcherNode.hasMouse():
            return
        self._drag_start = base.mouseWatcherNode.getMouse()
        self._orig_pos = self.window.getPos()
        try:
            base.taskMgr.add(self._drag_task, "debug-drag")
        except Exception:
            pass

    def _drag_task(self, task):
        if (
            self.window is None
            or self._drag_start is None
            or self._orig_pos is None
            or self.base is None
        ):
            return task.done
        base = self.base
        if not base.mouseWatcherNode.hasMouse():
            return task.cont
        cur = base.mouseWatcherNode.getMouse()
        dx = cur[0] - self._drag_start[0]
        dy = cur[1] - self._drag_start[1]
        self.window.setPos(self._orig_pos[0] + dx, 0, self._orig_pos[2] + dy)
        return task.cont
    def _end_drag(self, _evt: Any | None = None) -> None:
        self._drag_start = None
        self._orig_pos = None
        try:
            if self.base:
                self.base.taskMgr.remove("debug-drag")
        except Exception:
            pass
    def _stats(self):
        try:
            base = self.base
            if base is None:
                return 0, 0
            world = getattr(base, "world", None)
            if world is None:
                return 0, 0
            rm = world.region_manager
            regions = len(rm.loaded)
            geoms = base.render.findAllMatches("**/+GeomNode").getNumPaths()
            return regions, geoms
        except Exception:
            return 0, 0

    def dump_console(self):
        regions, geoms = self._stats()
        logger.info(
            f"{datetime.datetime.now().isoformat()} regions={regions} "
            f"geoms={geoms}"
        )

    def dump_file(self):
        regions, geoms = self._stats()
        if self.log_file is None:
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            self.log_file = LOG_DIR / f"debug_{ts}.txt"
        with self.log_file.open("a") as f:
            f.write(
                f"{datetime.datetime.now().isoformat()} {regions} {geoms}\n"
            )

    def toggle_pstats(self):
        try:
            if self.base and getattr(self.base, "pstats", None):
                self.base.stopPStats()
            elif self.base:
                self.base.startPStats("localhost", 5185)
        except Exception:
            pass

    def reload_region(self):
        try:
            if self.base is None:
                return
            base = self.base
            from runepy.world.region import world_to_region, Region
            from constants import REGION_SIZE
            world = getattr(base, "world", None)
            char = getattr(base, "character", None)
            if world is None or char is None:
                return
            x = int(char.model.getX())
            y = int(char.model.getY())
            rx, ry = world_to_region(x, y)
            region = world.region_manager.loaded.get((rx, ry))
            if region is None:
                return
            region.save()
            new_region = Region.load(rx, ry)
            new_region.make_mesh()
            parent = getattr(base, "tile_root", base.render)
            if new_region.node is not None:
                new_region.node.reparentTo(parent)
                new_region.node.setPos(rx * REGION_SIZE, ry * REGION_SIZE, 0)
            world.region_manager.loaded[(rx, ry)] = new_region
        except Exception:
            pass

    def get_avatar_speed(self) -> float:
        try:
            base = self.base
            if base is None:
                return 0.0
            return base.player.walk_speed
        except Exception:
            try:
                return base.character.speed
            except Exception:
                return 0.0

    def set_avatar_speed(self, value: float) -> None:
        try:
            base = self.base
            if base is None:
                return
            if hasattr(base.player, "set_speed"):
                base.player.set_speed(value)
            elif hasattr(base.character, "speed"):
                base.character.speed = value
        except Exception:
            pass

    def get_cam_pan_speed(self) -> float:
        try:
            base = self.base
            if base is None:
                return 0.0
            return base.camera_ctl.pan_speed
        except Exception:
            return 0.0

    def set_cam_pan_speed(self, value: float) -> None:
        try:
            if self.base:
                self.base.camera_ctl.set_pan_speed(value)
        except Exception:
            pass

    def get_zoom_step(self) -> float:
        try:
            return self.base.camera_ctl.zoom_step if self.base else 0.0
        except Exception:
            return 0.0

    def set_zoom_step(self, value: float) -> None:
        try:
            if self.base:
                self.base.camera_ctl.set_zoom_step(value)
        except Exception:
            pass

    def attach(self, base: Any | None) -> None:
        """Bind the debug GUI to an existing :class:`ShowBase` instance."""

        if base is None:
            return

        if getattr(self, "_attached", False):
            return  # guard against double attach
        self._attached = True

        self.base = base
        from .gui import DebugWindow
        self.window = DebugWindow(self)
        self.window.hide()  # start hidden

        base.accept('f1', self.window.toggleVisible)

        logger.info('[DebugManager] F1 bound')


_debug_instance: Optional[DebugManager] = None


def get_debug() -> DebugManager:
    """Return the shared :class:`DebugManager` instance."""
    global _debug_instance
    if _debug_instance is None:
        try:
            from direct.gui import DirectGui  # noqa: F401 - probe for Panda3D
            _debug_instance = DebugManager()
        except Exception:
            _debug_instance = NullDebugManager()  # type: ignore[assignment]
    return _debug_instance


__all__ = ["DebugManager", "get_debug"]
