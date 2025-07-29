from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple

from .array_map import RegionArrays
from .world.base_manager import BaseRegionManager


class MapManager(BaseRegionManager):
    """Load and unload regions around the player on demand."""

    def __init__(self, region_size: int = 64, view_distance: int = 1) -> None:
        super().__init__(region_size=region_size, view_radius=view_distance)
        self.current_region: Tuple[int, int] | None = None

    # ------------------------------------------------------------------
    # Coordinate helpers
    # ------------------------------------------------------------------
    def region_id(self, rx: int, ry: int) -> int:
        """Return a unique ID for region ``(rx, ry)``."""
        return (rx << 8) | ry

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

    def load_region(self, rx: int, ry: int) -> RegionArrays:
        """Load a region from disk or create an empty one."""
        file = Path(f"region_{rx}_{ry}.npz")
        if file.exists():
            return RegionArrays.load(str(file))
        return RegionArrays.empty()

    def unload_region(self, rx: int, ry: int) -> None:
        """Unload a region and optionally save it."""
        region = self.loaded.pop((rx, ry), None)
        if region is None:
            return
        file = Path(f"region_{rx}_{ry}.npz")
        region.save(str(file))

