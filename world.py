from panda3d.core import (
    BitMask32,
    CardMaker,
    CollisionNode,
    CollisionPlane,
    Plane,
    Point3,
    Vec3,
)
import random


class World:
    """Generate and display a simple grid-based world."""

    def __init__(self, render, radius=5, tile_size=1, debug=False):
        self.render = render
        self.radius = radius
        self.tile_size = tile_size
        self.debug = debug

        width = height = radius * 2 + 1
        self.grid = [[1 for _ in range(width)] for _ in range(height)]

        self.tile_root = self.render.attachNewNode("tile_root")
        self.tiles = {}

        self._generate_tiles()
        self.tile_root.flattenStrong()
        self._create_collision_plane()

    def log(self, *args, **kwargs):
        if self.debug:
            print(*args, **kwargs)

    def _generate_tiles(self):
        for x in range(-self.radius, self.radius + 1):
            for y in range(-self.radius, self.radius + 1):
                tile = self._create_tile((x * self.tile_size, y * self.tile_size, 0), self.tile_size)
                random_color = (random.random(), random.random(), random.random(), 1)
                tile.setColor(random_color)
                tile.setName(f"tile_{x}_{y}")
                self.tiles[(x, y)] = tile

    def _create_tile(self, position, size):
        card_maker = CardMaker("tile")
        card_maker.setFrame(-size / 2, size / 2, -size / 2, size / 2)
        tile = self.tile_root.attachNewNode(card_maker.generate())
        tile.setPos(*position)
        tile.setHpr(0, -90, 0)
        return tile

    def _create_collision_plane(self):
        plane = CollisionPlane(Plane(Vec3(0, 0, 1), Point3(0, 0, 0)))
        c_node = CollisionNode("grid_plane")
        c_node.addSolid(plane)
        c_node.set_into_collide_mask(BitMask32.all_on())
        self.render.attachNewNode(c_node)

