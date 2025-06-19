from runepy.utils import get_tile_from_mouse


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
        if self.client.options_menu.visible:
            return
        tile_x, tile_y = get_tile_from_mouse(self.client.mouseWatcherNode)
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
        if self.client.options_menu.visible:
            return
        tile_x, tile_y = get_tile_from_mouse(self.client.mouseWatcherNode)
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
        self.world.save_map(filename)

    def load_map(self, filename):
        """Load ``filename`` and rebuild the world's tiles."""
        self.world.load_map(filename)

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
