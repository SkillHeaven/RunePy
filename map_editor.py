class MapEditor:
    """Basic tile editing functionality."""

    def __init__(self, client, world):
        self.client = client
        self.world = world

    def register_bindings(self, key_manager):
        """Register editor actions with ``key_manager``."""
        key_manager.bind("toggle_tile", self.toggle_tile)
        key_manager.bind("toggle_interactable", self.toggle_interactable)
        key_manager.bind("save_map", self._hotkey_save)
        key_manager.bind("load_map", self._hotkey_load)

    def toggle_tile(self):
        tile_x, tile_y = self.client.get_tile_from_mouse()
        if tile_x is None:
            return
        grid_x = tile_x + self.world.radius
        grid_y = tile_y + self.world.radius
        if not (0 <= grid_x < len(self.world.grid[0]) and 0 <= grid_y < len(self.world.grid)):
            return
        tile_data = self.world.grid[grid_y][grid_x]
        tile_data.walkable = not tile_data.walkable
        tile = self.world.tiles.get((tile_x, tile_y))
        if tile:
            tile.setColor(self.world._tile_color(tile_data))

    def toggle_interactable(self):
        tile_x, tile_y = self.client.get_tile_from_mouse()
        if tile_x is None:
            return
        grid_x = tile_x + self.world.radius
        grid_y = tile_y + self.world.radius
        if not (0 <= grid_x < len(self.world.grid[0]) and 0 <= grid_y < len(self.world.grid)):
            return
        tile_data = self.world.grid[grid_y][grid_x]
        if "interactable" in tile_data.tags:
            tile_data.tags.remove("interactable")
        else:
            tile_data.tags.append("interactable")
        print(f"Tile ({tile_x}, {tile_y}) interactable tags: {tile_data.tags}")

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------
    def save_map(self, filename):
        """Write the current grid to ``filename`` as JSON."""
        import json

        def serialize(tile):
            return {
                "walkable": tile.walkable,
                "clickable": tile.clickable,
                "description": tile.description,
                "tags": tile.tags,
            }

        data = {
            "radius": self.world.radius,
            "tile_size": self.world.tile_size,
            "grid": [[serialize(t) for t in row] for row in self.world.grid],
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

        def deserialize(d):
            from world import TileData

            return TileData(
                walkable=d.get("walkable", True),
                clickable=d.get("clickable", True),
                description=d.get("description", ""),
                tags=d.get("tags", []),
            )

        loaded_grid = data.get("grid", [])
        if loaded_grid:
            self.world.grid = [[deserialize(t) for t in row] for row in loaded_grid]

        # Rebuild tiles from the loaded grid
        self.world.tile_root.removeNode()
        self.world.grid_lines.removeNode()
        self.world.tile_root = self.world.render.attachNewNode("tile_root")
        self.world.grid_lines = self.world.render.attachNewNode("grid_lines")
        self.world.tiles = {}
        self.world._generate_tiles()
        self.world._create_grid_lines()
        self.world.tile_root.flattenStrong()
        self.world.grid_lines.flattenStrong()

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
