from __future__ import annotations

import logging
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, ClassVar, Dict, List, Set, Tuple

import gzip
import numpy as np

from constants import REGION_SIZE, VIEW_RADIUS
from runepy.terrain import FLAG_BLOCKED

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
        Plane,
        Point3,
        Vec3,
        LineSegs,
        NodePath,
    )
    import direct.showbase.ShowBaseGlobal as sbg
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
        self.highlight_quad.setPos(x * self.tile_size, y * self.tile_size, 0.05)
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

        stitched = np.block(
            [
                [
                    ((self.region_manager.loaded[(rx + i, ry + j)].flags & FLAG_BLOCKED) == 0)
                    for i in (-1, 0, 1)
                ]
                for j in (-1, 0, 1)
            ]
        )

        offset_x = (rx - 1) * REGION_SIZE
        offset_y = (ry - 1) * REGION_SIZE
        return stitched.astype(int), offset_x, offset_y

    def shutdown(self) -> None:
        """Shut down the underlying :class:`RegionManager`."""
        self.region_manager.shutdown()


# ----------------------------------------------------------------------
# Region data structures
# ----------------------------------------------------------------------

def world_to_region(x: int, y: int) -> Tuple[int, int]:
    """Return ``(rx, ry)`` region coordinates for world position ``(x, y)``."""
    return x // REGION_SIZE, y // REGION_SIZE


def local_tile(x: int, y: int) -> Tuple[int, int]:
    """Return local tile indices within a region for world position ``(x, y)``."""
    return x % REGION_SIZE, y % REGION_SIZE


@dataclass
class Region:
    """Container for region tile data."""

    rx: int
    ry: int
    height: np.ndarray
    base: np.ndarray
    overlay: np.ndarray
    flags: np.ndarray
    node: "NodePath" | None = None

    FILE_VERSION: ClassVar[int] = 1

    @classmethod
    def load(cls, rx: int, ry: int) -> "Region":
        """Load region ``(rx, ry)`` from disk or create a new one."""
        path = Path("maps") / f"region_{rx}_{ry}.bin"
        size = REGION_SIZE * REGION_SIZE
        if path.exists():
            with gzip.open(path, "rb") as f:
                version = int.from_bytes(f.read(2), "little")
                if version != cls.FILE_VERSION:
                    raise ValueError(f"Unsupported region version {version}")
                height = np.frombuffer(f.read(size * 2), dtype=np.int16).reshape(REGION_SIZE, REGION_SIZE).copy()
                base = np.frombuffer(f.read(size), dtype=np.uint8).reshape(REGION_SIZE, REGION_SIZE).copy()
                overlay = np.frombuffer(f.read(size), dtype=np.uint8).reshape(REGION_SIZE, REGION_SIZE).copy()
                flags = np.frombuffer(f.read(size), dtype=np.uint8).reshape(REGION_SIZE, REGION_SIZE).copy()
        else:
            height = np.zeros((REGION_SIZE, REGION_SIZE), dtype=np.int16)
            base = np.zeros((REGION_SIZE, REGION_SIZE), dtype=np.uint8)
            overlay = np.zeros((REGION_SIZE, REGION_SIZE), dtype=np.uint8)
            flags = np.zeros((REGION_SIZE, REGION_SIZE), dtype=np.uint8)
        return cls(rx, ry, height, base, overlay, flags)

    def save(self) -> None:
        """Write this region back to disk."""
        path = Path("maps") / f"region_{self.rx}_{self.ry}.bin"
        path.parent.mkdir(parents=True, exist_ok=True)
        with gzip.open(path, "wb") as f:
            f.write(self.FILE_VERSION.to_bytes(2, "little"))
            f.write(self.height.astype(np.int16).tobytes())
            f.write(self.base.astype(np.uint8).tobytes())
            f.write(self.overlay.astype(np.uint8).tobytes())
            f.write(self.flags.astype(np.uint8).tobytes())

    def make_mesh(self):
        """Create or refresh a mesh for this region."""
        if GeomVertexFormat is None:
            return None
        if self.node is not None:
            self.node.removeNode()
            self.node = None
        # Include vertex colors so base/overlay arrays can influence rendering
        format = GeomVertexFormat.get_v3cp()
        vdata = GeomVertexData("region", format, Geom.UHStatic)
        vertex = GeomVertexWriter(vdata, "vertex")
        color = GeomVertexWriter(vdata, "color")
        tris = GeomTriangles(Geom.UHStatic)
        index = 0
        for y in range(REGION_SIZE):
            for x in range(REGION_SIZE):
                z = float(self.height[y, x])
                val = int(self.overlay[y, x]) or int(self.base[y, x])
                if val:
                    shade = val / 255.0
                    col = (shade, shade, shade, 1.0)
                else:
                    col = (0.2, 0.2, 0.2, 1.0)
                # Four identical vertices for a tile
                vertex.addData3(x, y, z)
                color.addData4f(*col)
                vertex.addData3(x + 1, y, z)
                color.addData4f(*col)
                vertex.addData3(x + 1, y + 1, z)
                color.addData4f(*col)
                vertex.addData3(x, y + 1, z)
                color.addData4f(*col)
                tris.addVertices(index, index + 1, index + 2)
                tris.addVertices(index, index + 2, index + 3)
                index += 4
        geom = Geom(vdata)
        geom.addPrimitive(tris)
        node = GeomNode("region")
        node.addGeom(geom)
        self.node = NodePath(node)
        return self.node


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
