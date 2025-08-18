from __future__ import annotations

import logging
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Dict, Tuple

from constants import REGION_SIZE, VIEW_RADIUS

from .base_manager import BaseRegionManager

try:
    import direct.showbase.ShowBaseGlobal as sbg
except Exception:  # pragma: no cover - Panda3D may be missing during tests
    sbg = None

from .region import Region

logger = logging.getLogger(__name__)


class RegionManager(BaseRegionManager):
    """Manage loading and unloading of :class:`Region` objects around a player."""

    def __init__(self, view_radius: int = VIEW_RADIUS, async_load: bool = False, cache_size: int | None = None) -> None:
        super().__init__(region_size=REGION_SIZE, view_radius=view_radius)
        self.async_load = async_load
        self._executor: ThreadPoolExecutor | None = None
        self._pending: Dict[Tuple[int, int], Future[Region]] = {}
        self.cache_size = cache_size
        self._cache: Dict[Tuple[int, int], Region] = {}
        if async_load:
            self._executor = ThreadPoolExecutor(max_workers=1)

    
    def clear_cache(self) -> None:
        """Empty the region cache."""
        self._cache.clear()

    # ------------------------------------------------------------------
    # Region helpers
    # ------------------------------------------------------------------
    def _setup_region(self, region: Region) -> Region:
        """Finalize region after loading by creating a mesh and parenting."""
        region.make_mesh()
        base_inst = getattr(sbg, "base", None)
        if region.node is not None and base_inst is not None and getattr(base_inst, "render", None) is not None:
            parent = getattr(base_inst, "tile_root", base_inst.render)
            region.node.reparentTo(parent)
            region.node.setPos(region.rx * REGION_SIZE, region.ry * REGION_SIZE, 0)
        return region

    def load_region(self, rx: int, ry: int) -> Region:
        """Synchronously load a region from disk, using the region cache if possible."""
        key = (rx, ry)
        region = self._cache.get(key)
        if region is None:
            region = Region.load(rx, ry)
            self._cache[key] = region
            if self.cache_size is not None and len(self._cache) > self.cache_size:
                self._cache.pop(next(iter(self._cache)))
        return self._setup_region(region)

    def unload_region(self, rx: int, ry: int) -> None:
        region = self.loaded.pop((rx, ry), None)
        if region is None:
            return
        if region.node is not None:
            region.node.removeNode()

    def ensure(self, player_x: int, player_y: int) -> None:
        """Ensure regions around ``(player_x, player_y)`` are loaded."""
        rx, ry = self.region_coords(player_x, player_y)
        want = self._wanted(rx, ry)

        for key in set(self.loaded) - want:
            self.unload_region(*key)
        for key in set(self._pending) - want:
            future = self._pending.pop(key)
            future.cancel()
        for key, future in list(self._pending.items()):
            if future.done():
                region = self._setup_region(future.result())
                self.loaded[key] = region
                self._pending.pop(key)
        for key in want - self.loaded.keys() - self._pending.keys():
            if self.async_load and self._executor is not None:
                self._pending[key] = self._executor.submit(Region.load, *key)
            else:
                self.loaded[key] = self.load_region(*key)

    def shutdown(self) -> None:
        """Clean up any executor threads used for async loading."""
        if self._executor is not None:
            self._executor.shutdown(wait=False)
            self._executor = None
