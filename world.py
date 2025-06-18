from dataclasses import dataclass, field
from typing import List


@dataclass
class TileData:
    """Metadata describing a single map tile."""

    walkable: bool = True
    clickable: bool = True
    description: str = ""
    tags: List[str] = field(default_factory=list)

from panda3d.core import (
    BitMask32,
    CardMaker,
    CollisionNode,
    CollisionPlane,
    Plane,
    Point3,
    Vec3,
    LineSegs,
)


class World:
    """Generate and display a simple grid-based world."""

    def __init__(self, render, radius=5, tile_size=1, debug=False):
        self.render = render
        self.radius = radius
        self.tile_size = tile_size
        self.debug = debug

        width = height = radius * 2 + 1
        self.grid = [[TileData() for _ in range(width)] for _ in range(height)]

        self.tile_root = self.render.attachNewNode("tile_root")
        self.tiles = {}
        self.grid_lines = self.render.attachNewNode("grid_lines")

        self._generate_tiles()
        self._create_grid_lines()
        self.tile_root.flattenStrong()
        self.grid_lines.flattenStrong()
        self._create_collision_plane()

    def log(self, *args, **kwargs):
        if self.debug:
            print(*args, **kwargs)

    def _tile_color(self, tile: TileData):
        """Return the display color for a tile based on its state."""
        if tile.walkable:
            return (0.3, 0.3, 0.3, 1)
        return (0.1, 0.1, 0.1, 1)

    def _generate_tiles(self):
        for x in range(-self.radius, self.radius + 1):
            for y in range(-self.radius, self.radius + 1):
                tile = self._create_tile((x * self.tile_size, y * self.tile_size, 0), self.tile_size)
                tile_data = self.grid[y + self.radius][x + self.radius]
                tile.setColor(self._tile_color(tile_data))

                tile.setName(f"tile_{x}_{y}")
                self.tiles[(x, y)] = tile

    def _create_tile(self, position, size):
        card_maker = CardMaker("tile")
        card_maker.setFrame(-size / 2, size / 2, -size / 2, size / 2)
        tile = self.tile_root.attachNewNode(card_maker.generate())
        tile.setPos(*position)
        tile.setHpr(0, -90, 0)
        return tile

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

    def _create_collision_plane(self):
        plane = CollisionPlane(Plane(Vec3(0, 0, 1), Point3(0, 0, 0)))
        c_node = CollisionNode("grid_plane")
        c_node.addSolid(plane)
        c_node.set_into_collide_mask(BitMask32.all_on())
        self.render.attachNewNode(c_node)

