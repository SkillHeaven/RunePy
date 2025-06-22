from dataclasses import dataclass, field
from typing import List, Dict, Any


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
    )
except Exception:  # pragma: no cover - Panda3D may be missing during tests
    BitMask32 = CardMaker = CollisionNode = CollisionPlane = Plane = None
    Point3 = Vec3 = LineSegs = None
    Geom = GeomNode = GeomTriangles = None
    GeomVertexData = GeomVertexFormat = GeomVertexWriter = None


class World:
    """Generate and display a simple grid-based world."""

    def __init__(self, render, radius=500, tile_size=1, debug=False, map_file=None):
        self.render = render
        self.radius = radius
        self.tile_size = tile_size
        self.debug = debug

        width = height = radius * 2 + 1
        self.grid = [[TileData() for _ in range(width)] for _ in range(height)]

        if map_file:
            try:
                self.load_map(map_file)
            except Exception as exc:
                self.log(f"Failed to load map '{map_file}': {exc}")

        self.tile_root = self.render.attachNewNode("tile_root")
        self.grid_lines = self.render.attachNewNode("grid_lines")

        self._generate_tiles()
        self._create_grid_lines()
        self._create_subfloor()

        # Highlight quad reused for hover effects
        self.highlight_quad = self._create_highlight_quad()
        # Flattening tiles would merge them into a single node which prevents
        # per-tile color adjustments. Keep tiles separate so each can be
        # highlighted individually. Grid lines remain flattened for performance.
        self.grid_lines.flattenStrong()

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


    def save_map(self, filename):
        """Write the current grid to ``filename`` as JSON."""
        import json

        data = {
            "radius": self.radius,
            "tile_size": self.tile_size,
            "grid": [[tile.to_dict() for tile in row] for row in self.grid],
        }
        with open(filename, "w") as f:
            json.dump(data, f)

    def log(self, *args, **kwargs):
        if self.debug:
            print(*args, **kwargs)

    def _tile_color(self, tile: TileData):
        """Return the display color for a tile based on its state."""
        if tile.walkable:
            return (0.3, 0.3, 0.3, 1)
        return (0.1, 0.1, 0.1, 1)

    def _generate_tiles(self):
        if CardMaker is None:
            return

        format = GeomVertexFormat.get_v3cp()
        vdata = GeomVertexData("tiles", format, Geom.UHDynamic)
        vertex = GeomVertexWriter(vdata, "vertex")
        color = GeomVertexWriter(vdata, "color")
        tris = GeomTriangles(Geom.UHDynamic)

        self._tile_indices = {}
        index = 0
        half = self.tile_size / 2
        for x in range(-self.radius, self.radius + 1):
            for y in range(-self.radius, self.radius + 1):
                x0 = x * self.tile_size - half
                x1 = x * self.tile_size + half
                y0 = y * self.tile_size - half
                y1 = y * self.tile_size + half
                tile_data = self.grid[y + self.radius][x + self.radius]
                col = self._tile_color(tile_data)

                vertex.addData3(x0, y0, 0)
                color.addData4(*col)
                vertex.addData3(x1, y0, 0)
                color.addData4(*col)
                vertex.addData3(x1, y1, 0)
                color.addData4(*col)
                vertex.addData3(x0, y1, 0)
                color.addData4(*col)

                tris.addVertices(index, index + 1, index + 2)
                tris.addVertices(index, index + 2, index + 3)

                self._tile_indices[(x, y)] = (index, index + 1, index + 2, index + 3)
                index += 4

        geom = Geom(vdata)
        geom.addPrimitive(tris)
        node = GeomNode("tiles")
        node.addGeom(geom)
        self.tile_geom = self.tile_root.attachNewNode(node)

    def update_tile_color(self, x: int, y: int) -> None:
        if CardMaker is None:
            return
        indices = self._tile_indices.get((x, y))
        if not indices:
            return
        vdata = self.tile_geom.node().modifyGeom(0).modifyVertexData()
        writer = GeomVertexWriter(vdata, "color")
        col = self._tile_color(self.grid[y + self.radius][x + self.radius])
        for i in indices:
            writer.setRow(i)
            writer.setData4f(*col)

    def _create_grid_lines(self):
        lines = LineSegs()
        lines.setThickness(1.0)
        lines.setColor(0.2, 0.2, 0.2, 1)

        start = -self.radius - 0.5
        end = self.radius + 0.5

        for i in range(self.radius * 2 + 2):
            pos = start + i
            x = pos * self.tile_size
            lines.moveTo(x, start * self.tile_size, 0.02)
            lines.drawTo(x, end * self.tile_size, 0.02)

        for i in range(self.radius * 2 + 2):
            pos = start + i
            y = pos * self.tile_size
            lines.moveTo(start * self.tile_size, y, 0.02)
            lines.drawTo(end * self.tile_size, y, 0.02)

        node = lines.create()
        self.grid_lines.attachNewNode(node)

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
    def load_map(self, filename):
        """Load ``filename`` and rebuild this world's tiles."""
        import json

        with open(filename, "r") as f:
            data = json.load(f)

        self.radius = data.get("radius", self.radius)
        self.tile_size = data.get("tile_size", self.tile_size)

        loaded_grid = data.get("grid", [])
        if loaded_grid:
            self.grid = [
                [TileData.from_dict(t) for t in row]
                for row in loaded_grid
            ]

        # Rebuild tile nodes from loaded grid
        self.tile_root.removeNode()
        self.grid_lines.removeNode()
        self.tile_root = self.render.attachNewNode("tile_root")
        self.grid_lines = self.render.attachNewNode("grid_lines")
        self._generate_tiles()
        self._create_grid_lines()
        # Keep tiles un-flattened so hover highlighting works on individual
        # nodes. Grid lines can still be flattened for efficiency.
        self.grid_lines.flattenStrong()


