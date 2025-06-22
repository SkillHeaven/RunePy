"""Debug utilities for RunePy.

This module exposes a :class:`DebugManager` singleton via :func:`get_debug`.
Importing the package will not raise ImportError even if Panda3D's ``direct``
module is unavailable.
"""

from __future__ import annotations
from pathlib import Path
import datetime

from typing import Optional, Any

try:
    from .gui import DebugWindow  # type: ignore
except Exception:  # pragma: no cover - GUI components may not be present
    DebugWindow = None  # type: ignore

class NullDebugManager:
    """Fallback manager used when Panda3D is unavailable."""

    def __init__(self) -> None:
        self.window = None

    def attach(self, base: Any | None = None) -> None:
        pass

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
        self.window: Optional[DebugWindow] = None
        if DebugWindow is not None:
            try:
                self.window = DebugWindow(self)
                try:
                    from direct.showbase.ShowBaseGlobal import base
                    from direct.gui.DirectGui import DirectGuiGlobals as DGG
                    base.accept('f1', self.window.toggleVisible)
                    self.window.bind(DGG.B1PRESS, self._start_drag)
                    self.window.bind(DGG.B1RELEASE, self._end_drag)
                except Exception:
                    pass
            except Exception:
                # Failed to initialize debug window (likely no Panda3D)
                self.window = None
        self._drag_start = None
        self._orig_pos = None

    def enable(self) -> None:
        if self.window is None:
            return
        try:
            from direct.showbase.ShowBaseGlobal import taskMgr
            taskMgr.doMethodLater(0.5, self.window.refresh_task, "dbg-refresh")
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
        if self.window is None:
            return
        try:
            from direct.showbase.ShowBaseGlobal import base
        except Exception:
            return
        if not base.mouseWatcherNode.hasMouse():
            return
        self._drag_start = base.mouseWatcherNode.getMouse()
        self._orig_pos = self.window.getPos()
        try:
            base.taskMgr.add(self._drag_task, "debug-drag")
        except Exception:
            pass

    def _drag_task(self, task):
        if self.window is None or self._drag_start is None or self._orig_pos is None:
            return task.done
        try:
            from direct.showbase.ShowBaseGlobal import base
        except Exception:
            return task.done
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
            from direct.showbase.ShowBaseGlobal import base
            base.taskMgr.remove("debug-drag")
        except Exception:
            pass


    def _stats(self):
        try:
            from direct.showbase.ShowBaseGlobal import base, render
            world = getattr(base, "world", None)
            if world is None:
                return 0, 0
            rm = world.region_manager
            regions = len(rm.loaded)
            geoms = render.findAllMatches("**/+GeomNode").getNumPaths()
            return regions, geoms
        except Exception:
            return 0, 0

    def dump_console(self):
        regions, geoms = self._stats()
        print(f"{datetime.datetime.now().isoformat()} regions={regions} geoms={geoms}")

    def dump_file(self):
        regions, geoms = self._stats()
        if self.log_file is None:
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            self.log_file = Path(f"debug_{ts}.txt")
        with self.log_file.open("a") as f:
            f.write(f"{datetime.datetime.now().isoformat()} {regions} {geoms}\n")

    def toggle_pstats(self):
        try:
            from direct.showbase.ShowBaseGlobal import base
            if getattr(base, "pstats", None):
                base.stopPStats()
            else:
                base.startPStats("localhost", 5185)
        except Exception:
            pass

    def reload_region(self):
        try:
            from direct.showbase.ShowBaseGlobal import base
            from runepy.world import world_to_region, Region, REGION_SIZE
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

    def attach(self, base: Any) -> None:
        """Hook the debug window into the running ShowBase instance."""
        self.enable()

_debug_instance: Optional[DebugManager] = None


def get_debug() -> DebugManager:
    """Return the shared :class:`DebugManager` instance."""
    global _debug_instance
    if _debug_instance is None:
        if DebugWindow is None:
            _debug_instance = NullDebugManager()  # type: ignore[assignment]
        else:
            try:
                _debug_instance = DebugManager()
            except Exception:
                _debug_instance = NullDebugManager()  # type: ignore[assignment]
    return _debug_instance


__all__ = ["DebugManager", "get_debug"]
