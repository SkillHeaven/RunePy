from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple

import numpy as np

from constants import REGION_SIZE
from runepy.terrain import FLAG_BLOCKED

from .manager import RegionManager
from .region import local_tile, world_to_region

logger = logging.getLogger(__name__)


@dataclass
class TileData:
    """Metadata describing a single map tile."""

    walkable: bool = True
    clickable: bool = True
    description: str = ""
    tags: List[str] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize this ``TileData`` into a dictionary."""
        data = {
            "walkable": self.walkable,
            "clickable": self.clickable,
            "description": self.description,
            "tags": self.tags,
        }
        data.update(self.properties)
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TileData":
        """Create a ``TileData`` instance from ``data``."""
        known = {
            "walkable": data.get("walkable", True),
            "clickable": data.get("clickable", True),
            "description": data.get("description", ""),
            "tags": data.get("tags", []),
        }
        extras = {
            k: v
            for k, v in data.items()
            if k not in {"walkable", "clickable", "description", "tags"}
        }
        tile = cls(**known)
        tile.properties.update(extras)
        return tile

try:
    import direct.showbase.ShowBaseGlobal as sbg
    from panda3d.core import (
        BitMask32,
        CardMaker,
        CollisionNode,
        CollisionPlane,
        Geom,
        GeomNode,
        GeomTriangles,
        GeomVertexData,
        GeomVertexFormat,
        GeomVertexWriter,
        LineSegs,
        NodePath,
        Plane,
        Point3,
        Vec3,
    )
except Exception:  # pragma: no cover - Panda3D may be missing during tests
    BitMask32 = CardMaker = CollisionNode = CollisionPlane = Plane = None
    Point3 = Vec3 = LineSegs = NodePath = None
    Geom = GeomNode = GeomTriangles = None
    GeomVertexData = GeomVertexFormat = GeomVertexWriter = None
    sbg = None


class World:
    """Generate and display a simple grid-based world."""

    def __init__(
        self,
        render=None,
        radius=None,
        tile_size=1,
        debug=False,
        progress_callback=None,
        view_radius=1,
    ):
        self.render = render
        if radius is None:
            radius = view_radius * REGION_SIZE
        self.radius = radius
        self.tile_size = tile_size
        self.debug = debug
        self.progress_callback = progress_callback

        self.region_manager = RegionManager(view_radius=view_radius)
        self.manager = self.region_manager
        self._current_region: Tuple[int, int] | None = None
        if self.render is not None:
            self.tile_root = self.render.attachNewNode("tile_root")
            base_inst = getattr(sbg, "base", None)
            if base_inst is not None:
                base_inst.tile_root = self.tile_root
            self._create_subfloor()
            if self.progress_callback:
                self.progress_callback(1.0, "World ready")

            # Highlight quad reused for hover effects
            self.highlight_quad = self._create_highlight_quad()
        else:
            self.tile_root = None
            self.highlight_quad = None

        self._hovered = None

    def _create_subfloor(self):
        """Create a large black plane just below the tiles."""
        if CardMaker is None:
            return
        plane_size = (self.radius * 2 + 4) * self.tile_size
        cm = CardMaker("subfloor")
        cm.setFrame(-plane_size / 2, plane_size / 2, -plane_size / 2, plane_size / 2)
        node = self.render.attachNewNode(cm.generate())
        node.setPos(0, 0, -1)
        node.setColor(0, 0, 0, 1)
        # Ensure the subfloor renders before the tiles
        node.setBin("background", 0)
        node.setDepthWrite(False)
    def _create_highlight_quad(self):
        cm = CardMaker("highlight")
        size = self.tile_size * 0.9
        cm.setFrame(-size/2, size/2, -size/2, size/2)
        quad = self.tile_root.attachNewNode(cm.generate())
        quad.setHpr(0, -90, 0)
        quad.setColor(1, 1, 0, 0.5)
        quad.setTransparency(True)
        quad.hide()
        return quad



    def log(self, *args, **kwargs):
        if self.debug:
            logger.debug(*args, **kwargs)



    def highlight_tile(self, x: int, y: int):
        """Highlight tile at (x, y) by moving the overlay quad."""
        coord = (x, y)
        if self._hovered == coord:
            return
        self.highlight_quad.setPos(
            (x + 0.5) * self.tile_size, (y + 0.5) * self.tile_size, 0.05
        )
        self.highlight_quad.show()
        self._hovered = coord

    def clear_highlight(self):
        """Hide the highlight overlay."""
        self.highlight_quad.hide()
        self._hovered = None

    def _create_collision_plane(self):
        plane = CollisionPlane(Plane(Vec3(0, 0, 1), Point3(0, 0, 0)))
        c_node = CollisionNode("grid_plane")
        c_node.addSolid(plane)
        c_node.set_into_collide_mask(BitMask32.all_on())
        self.render.attachNewNode(c_node)

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # Region streaming helpers
    # ------------------------------------------------------------------
    def update_streaming(self, player_x: int, player_y: int) -> None:
        """Ensure surrounding regions for ``(player_x, player_y)`` are loaded."""
        rx, ry = world_to_region(player_x, player_y)
        if self._current_region != (rx, ry):
            self._current_region = (rx, ry)
            self.region_manager.ensure(player_x, player_y)

    def is_walkable(self, x: int, y: int) -> bool:
        """Return ``True`` if tile ``(x, y)`` is not flagged as blocked."""
        rx, ry = world_to_region(x, y)
        region = self.region_manager.loaded.get((rx, ry))
        if region is None:
            self.region_manager.ensure(x, y)
            region = self.region_manager.loaded.get((rx, ry))
            if region is None:
                return False
        lx, ly = local_tile(x, y)
        return not bool(region.flags[ly, lx] & FLAG_BLOCKED)

    def walkable_window(self, center_x: int, center_y: int) -> tuple[np.ndarray, int, int]:
        """Return a ``(192, 192)`` walkability matrix around ``center_x, center_y``.

        The matrix is stitched together from the 3 × 3 loaded regions surrounding
        the provided coordinates. The accompanying offsets translate local path
        coordinates back into world space.
        """
        rx, ry = world_to_region(center_x, center_y)
        # Ensure regions around the center are present
        self.region_manager.ensure(center_x, center_y)

        size = REGION_SIZE
        stitched = np.empty((size * 3, size * 3), dtype=bool)

        for row, j in enumerate((-1, 0, 1)):
            for col, i in enumerate((-1, 0, 1)):
                flags = self.region_manager.loaded[(rx + i, ry + j)].flags
                region_mask = (flags & FLAG_BLOCKED) == 0
                stitched[
                    row * size : (row + 1) * size,
                    col * size : (col + 1) * size,
                ] = region_mask

        offset_x = (rx - 1) * REGION_SIZE
        offset_y = (ry - 1) * REGION_SIZE
        return stitched.astype(int), offset_x, offset_y

    def shutdown(self) -> None:
        """Shut down the underlying :class:`RegionManager`."""
        self.region_manager.shutdown()
