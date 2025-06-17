class MapEditor:
    """Basic tile editing functionality."""

    def __init__(self, client, world):
        self.client = client
        self.world = world
        client.accept("mouse3", self.toggle_tile)

    def toggle_tile(self):
        tile_x, tile_y = self.client.get_tile_from_mouse()
        if tile_x is None:
            return
        grid_x = tile_x + self.world.radius
        grid_y = tile_y + self.world.radius
        if not (0 <= grid_x < len(self.world.grid[0]) and 0 <= grid_y < len(self.world.grid)):
            return
        current = self.world.grid[grid_y][grid_x]
        new_value = 0 if current else 1
        self.world.grid[grid_y][grid_x] = new_value
        tile = self.world.tiles.get((tile_x, tile_y))
        if tile:
            color = (0.2, 0.2, 0.2, 1) if new_value == 0 else (1, 1, 1, 1)
            tile.setColor(color)
