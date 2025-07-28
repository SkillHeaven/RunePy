from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple

from .array_map import RegionArrays


class MapManager:
    """Load and unload regions around the player on demand."""

    def __init__(self, region_size: int = 64, view_distance: int = 1):
        self.region_size = region_size
        self.view_distance = view_distance
        self.loaded: Dict[Tuple[int, int], RegionArrays] = {}
        self.current_region: Tuple[int, int] | None = None

    # ------------------------------------------------------------------
    # Coordinate helpers
    # ------------------------------------------------------------------
    def region_coords(self, x: int, y: int) -> Tuple[int, int]:
        """Return ``(Rx, Ry)`` for ``(x, y)`` world coordinates."""
        return x // self.region_size, y // self.region_size

    def region_id(self, rx: int, ry: int) -> int:
        """Return a unique ID for region ``(rx, ry)``."""
        return (rx << 8) | ry

    def local_coords(self, x: int, y: int) -> Tuple[int, int]:
        """Return tile indices within its region."""
        return x % self.region_size, y % self.region_size

    # ------------------------------------------------------------------
    # Loading logic
    # ------------------------------------------------------------------
    def update(self, x: int, y: int) -> None:
        """Update loaded regions based on player position ``(x, y)``."""
        rx, ry = self.region_coords(x, y)
        if self.current_region == (rx, ry):
            return
        self.current_region = (rx, ry)
        self._ensure_loaded(rx, ry)

    def _ensure_loaded(self, rx: int, ry: int) -> None:
        keep = set()
        for i in range(rx - self.view_distance, rx + self.view_distance + 1):
            for j in range(
                ry - self.view_distance,
                ry + self.view_distance + 1,
            ):
                keep.add((i, j))
                if (i, j) not in self.loaded:
                    self.loaded[(i, j)] = self.load_region(i, j)
        for key in list(self.loaded.keys()):
            if key not in keep:
                self.unload_region(*key)

    def load_region(self, rx: int, ry: int) -> RegionArrays:
        """Load a region from disk or create an empty one."""
        file = Path(f"region_{rx}_{ry}.npz")
        if file.exists():
            region = RegionArrays.load(str(file))
        else:
            region = RegionArrays.empty()
        self.loaded[(rx, ry)] = region
        return region

    def unload_region(self, rx: int, ry: int) -> None:
        """Unload a region and optionally save it."""
        region = self.loaded.pop((rx, ry), None)
        if region is None:
            return
        file = Path(f"region_{rx}_{ry}.npz")
        region.save(str(file))

