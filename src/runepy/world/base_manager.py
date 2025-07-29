from __future__ import annotations

from typing import Any, Dict, Set, Tuple

from constants import REGION_SIZE, VIEW_RADIUS


class BaseRegionManager:
    """Base helper implementing region coordinate math and loading logic."""

    def __init__(self, region_size: int = REGION_SIZE, view_radius: int = VIEW_RADIUS) -> None:
        self.region_size = region_size
        self.view_radius = view_radius
        self.loaded: Dict[Tuple[int, int], Any] = {}

    # ------------------------------------------------------------------
    # Coordinate helpers
    # ------------------------------------------------------------------
    def region_coords(self, x: int, y: int) -> Tuple[int, int]:
        """Return ``(rx, ry)`` for world coordinates ``(x, y)``."""
        return x // self.region_size, y // self.region_size

    def local_coords(self, x: int, y: int) -> Tuple[int, int]:
        """Return local tile indices within a region."""
        return x % self.region_size, y % self.region_size

    # ------------------------------------------------------------------
    # Loading logic helpers
    # ------------------------------------------------------------------
    def _wanted(self, rx: int, ry: int) -> Set[Tuple[int, int]]:
        r = range(-self.view_radius, self.view_radius + 1)
        return {(rx + i, ry + j) for i in r for j in r}

    def _ensure_loaded(self, rx: int, ry: int) -> None:
        """Ensure regions around ``(rx, ry)`` are loaded."""
        want = self._wanted(rx, ry)
        for coord in want:
            if coord not in self.loaded:
                self.loaded[coord] = self.load_region(*coord)
        for coord in list(self.loaded.keys()):
            if coord not in want:
                self.unload_region(*coord)

    # ------------------------------------------------------------------
    # Methods expected to be provided by subclasses
    # ------------------------------------------------------------------
    def load_region(self, rx: int, ry: int):
        raise NotImplementedError

    def unload_region(self, rx: int, ry: int) -> None:
        raise NotImplementedError
