"""Debug utilities for RunePy.

This module exposes a :class:`DebugManager` singleton via :func:`get_debug`.
Importing the package will not raise ImportError even if Panda3D's ``direct``
module is unavailable.
"""

from __future__ import annotations
from pathlib import Path
import datetime

from typing import Optional

try:
    from .gui import DebugWindow  # type: ignore
except Exception:  # pragma: no cover - GUI components may not be present
    DebugWindow = None  # type: ignore


class DebugManager:
    """Simple container for debug helpers."""

    def __init__(self) -> None:
        self.log_file: Optional[Path] = None
        self.window: Optional[DebugWindow] = None
        if DebugWindow is not None:
            try:
                self.window = DebugWindow(self)
            except Exception:
                # Failed to initialize debug window (likely no Panda3D)
                self.window = None

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

_debug_instance: Optional[DebugManager] = None


def get_debug() -> DebugManager:
    """Return the shared :class:`DebugManager` instance."""
    global _debug_instance
    if _debug_instance is None:
        _debug_instance = DebugManager()
    return _debug_instance


__all__ = ["DebugManager", "get_debug"]
