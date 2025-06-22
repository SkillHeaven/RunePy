from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor
from typing import Dict, Tuple, Set

from constants import VIEW_RADIUS
from .coords import world_to_region
from .region import Region


class RegionManager:
    """Manage loading and unloading of ``Region`` objects around a player."""

    def __init__(self, view_radius: int = VIEW_RADIUS, async_load: bool = False) -> None:
        self.loaded: Dict[Tuple[int, int], Region] = {}
        self.view_radius = view_radius
        self.async_load = async_load
        self._executor: ThreadPoolExecutor | None = None
        self._pending: Dict[Tuple[int, int], Future[Region]] = {}
        if async_load:
            self._executor = ThreadPoolExecutor(max_workers=1)

    # ------------------------------------------------------------------
    def _wanted(self, rx: int, ry: int) -> Set[Tuple[int, int]]:
        r = range(-self.view_radius, self.view_radius + 1)
        return {(rx + i, ry + j) for i in r for j in r}

    # ------------------------------------------------------------------
    def ensure(self, player_x: int, player_y: int) -> None:
        """Ensure regions around ``(player_x, player_y)`` are loaded."""
        rx, ry = world_to_region(player_x, player_y)
        want = self._wanted(rx, ry)

        # Remove regions that are no longer needed
        for key in set(self.loaded) - want:
            region = self.loaded.pop(key)
            if region.node is not None:
                region.node.removeNode()
        # Cancel outstanding loads for regions we no longer care about
        for key in set(self._pending) - want:
            future = self._pending.pop(key)
            future.cancel()

        # Finalize any pending loads that completed
        for key, future in list(self._pending.items()):
            if future.done():
                region = future.result()
                region.make_mesh()
                self.loaded[key] = region
                self._pending.pop(key)

        # Queue or perform loads for any missing regions
        for key in want - self.loaded.keys() - self._pending.keys():
            if self.async_load and self._executor is not None:
                self._pending[key] = self._executor.submit(Region.load, *key)
            else:
                region = Region.load(*key)
                region.make_mesh()
                self.loaded[key] = region

    # ------------------------------------------------------------------
    def shutdown(self) -> None:
        """Clean up any executor threads used for async loading."""
        if self._executor is not None:
            self._executor.shutdown(wait=False)
            self._executor = None
