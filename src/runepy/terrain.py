from dataclasses import dataclass
from typing import Tuple


#: Tile flag bitmask for a blocked or non-walkable tile
FLAG_BLOCKED = 0x1


@dataclass
class TerrainTile:
    """Tile information used for terrain rendering and collision."""

    corner_heights: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0)
    underlay_id: int = 0
    overlay_id: int = 0
    overlay_shape: int = 0
    overlay_rotation: int = 0
    flags: int = 0

    @property
    def walkable(self) -> bool:
        """Return ``True`` if the tile is not marked as blocked."""
        return not bool(self.flags & FLAG_BLOCKED)

