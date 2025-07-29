from __future__ import annotations

import logging
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Dict, Set, Tuple

from constants import REGION_SIZE, VIEW_RADIUS

try:
    import direct.showbase.ShowBaseGlobal as sbg
except Exception:  # pragma: no cover - Panda3D may be missing during tests
    sbg = None

from .region import Region, world_to_region

logger = logging.getLogger(__name__)


class RegionManager:
    """Manage loading and unloading of :class:`Region` objects around a player."""

    def __init__(self, view_radius: int = VIEW_RADIUS, async_load: bool = False) -> None:
        self.loaded: Dict[Tuple[int, int], Region] = {}
        self.view_radius = view_radius
        self.async_load = async_load
        self._executor: ThreadPoolExecutor | None = None
        self._pending: Dict[Tuple[int, int], Future[Region]] = {}
        if async_load:
            self._executor = ThreadPoolExecutor(max_workers=1)

    def _wanted(self, rx: int, ry: int) -> Set[Tuple[int, int]]:
        r = range(-self.view_radius, self.view_radius + 1)
        return {(rx + i, ry + j) for i in r for j in r}

    def ensure(self, player_x: int, player_y: int) -> None:
        """Ensure regions around ``(player_x, player_y)`` are loaded."""
        rx, ry = world_to_region(player_x, player_y)
        want = self._wanted(rx, ry)

        for key in set(self.loaded) - want:
            region = self.loaded.pop(key)
            if region.node is not None:
                region.node.removeNode()
        for key in set(self._pending) - want:
            future = self._pending.pop(key)
            future.cancel()
        for key, future in list(self._pending.items()):
            if future.done():
                region = future.result()
                region.make_mesh()
                base_inst = getattr(sbg, "base", None)
                if region.node is not None and base_inst is not None and getattr(base_inst, "render", None) is not None:
                    parent = getattr(base_inst, "tile_root", base_inst.render)
                    region.node.reparentTo(parent)
                    region.node.setPos(region.rx * REGION_SIZE, region.ry * REGION_SIZE, 0)
                self.loaded[key] = region
                self._pending.pop(key)
        for key in want - self.loaded.keys() - self._pending.keys():
            if self.async_load and self._executor is not None:
                self._pending[key] = self._executor.submit(Region.load, *key)
            else:
                region = Region.load(*key)
                region.make_mesh()
                base_inst = getattr(sbg, "base", None)
                if region.node is not None and base_inst is not None and getattr(base_inst, "render", None) is not None:
                    parent = getattr(base_inst, "tile_root", base_inst.render)
                    region.node.reparentTo(parent)
                    region.node.setPos(region.rx * REGION_SIZE, region.ry * REGION_SIZE, 0)
                self.loaded[key] = region

    def shutdown(self) -> None:
        """Clean up any executor threads used for async loading."""
        if self._executor is not None:
            self._executor.shutdown(wait=False)
            self._executor = None
