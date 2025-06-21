from dataclasses import dataclass
from typing import Tuple

import numpy as np


@dataclass
class RegionArrays:
    """Container for tile layers stored as ``numpy`` arrays."""

    height_map: np.ndarray
    terrain_ids: np.ndarray
    overlay_ids: np.ndarray
    collision_mask: np.ndarray

    @classmethod
    def empty(cls, shape: Tuple[int, int] = (64, 64)) -> "RegionArrays":
        """Return a new ``RegionArrays`` filled with zeros."""
        return cls(
            height_map=np.zeros(shape, dtype=np.int16),
            terrain_ids=np.zeros(shape, dtype=np.uint8),
            overlay_ids=np.zeros(shape, dtype=np.uint8),
            collision_mask=np.zeros(shape, dtype=bool),
        )

    def save(self, filename: str) -> None:
        """Save all layers to ``filename`` as an ``.npz`` archive."""
        np.savez(
            filename,
            height_map=self.height_map,
            terrain_ids=self.terrain_ids,
            overlay_ids=self.overlay_ids,
            collision_mask=self.collision_mask,
        )

    @classmethod
    def load(cls, filename: str) -> "RegionArrays":
        """Load layers from ``filename`` previously saved with :meth:`save`."""
        data = np.load(filename)
        return cls(
            data["height_map"],
            data["terrain_ids"],
            data["overlay_ids"],
            data["collision_mask"],
        )

