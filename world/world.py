from __future__ import annotations

from .coords import world_to_region, local_tile
from .region_manager import RegionManager
from runepy.terrain import FLAG_BLOCKED


class World:
    """World that streams regions using :class:`RegionManager`."""

    def __init__(self, view_radius: int = 1) -> None:
        self.manager = RegionManager(view_radius=view_radius)
        self._current_region: tuple[int, int] | None = None

    # ------------------------------------------------------------------
    def update_streaming(self, player_x: int, player_y: int) -> None:
        """Ensure surrounding regions for ``(player_x, player_y)`` are loaded."""
        rx, ry = world_to_region(player_x, player_y)
        if self._current_region != (rx, ry):
            self._current_region = (rx, ry)
            self.manager.ensure(player_x, player_y)

    # ------------------------------------------------------------------
    def is_walkable(self, x: int, y: int) -> bool:
        """Return ``True`` if tile ``(x, y)`` is not flagged as blocked."""
        rx, ry = world_to_region(x, y)
        region = self.manager.loaded.get((rx, ry))
        if region is None:
            self.manager.ensure(x, y)
            region = self.manager.loaded.get((rx, ry))
            if region is None:
                return False
        lx, ly = local_tile(x, y)
        return not bool(region.flags[ly, lx] & FLAG_BLOCKED)

    # ------------------------------------------------------------------
    def shutdown(self) -> None:
        """Shut down the underlying :class:`RegionManager`."""
        self.manager.shutdown()
