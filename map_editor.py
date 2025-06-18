class MapEditor:
    """Basic tile editing functionality."""

    def __init__(self, client, world):
        self.client = client
        self.world = world
        client.accept("mouse3", self.toggle_tile)

        # Convenience keybindings for saving/loading the map when running the
        # editor as a standalone application. These will simply print an error
        # if invoked when the client does not provide the corresponding methods.
        client.accept("s", self._hotkey_save)
        client.accept("l", self._hotkey_load)

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

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------
    def save_map(self, filename):
        """Write the current grid to ``filename`` as JSON."""
        import json

        data = {
            "radius": self.world.radius,
            "tile_size": self.world.tile_size,
            "grid": self.world.grid,
        }
        with open(filename, "w") as f:
            json.dump(data, f)

    def load_map(self, filename):
        """Load ``filename`` and rebuild the world's tiles."""
        import json

        with open(filename, "r") as f:
            data = json.load(f)

        self.world.radius = data.get("radius", self.world.radius)
        self.world.tile_size = data.get("tile_size", self.world.tile_size)
        self.world.grid = data.get("grid", self.world.grid)

        # Rebuild tiles from the loaded grid
        self.world.tile_root.removeNode()
        self.world.tile_root = self.world.render.attachNewNode("tile_root")
        self.world.tiles = {}
        self.world._generate_tiles()
        self.world.tile_root.flattenStrong()

    # ------------------------------------------------------------------
    # Hotkeys used when running the editor standalone
    # ------------------------------------------------------------------
    def _hotkey_save(self):
        if hasattr(self, "save_callback"):
            self.save_callback()
        else:
            try:
                self.save_map("map.json")
                print("Map saved to map.json")
            except Exception as exc:
                print(f"Failed to save map: {exc}")

    def _hotkey_load(self):
        if hasattr(self, "load_callback"):
            self.load_callback()
        else:
            try:
                self.load_map("map.json")
                print("Map loaded from map.json")
            except Exception as exc:
                print(f"Failed to load map: {exc}")
