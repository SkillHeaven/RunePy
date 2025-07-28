from runepy.utils import get_tile_from_mouse
from runepy.world import world_to_region, local_tile
from runepy.terrain import FLAG_BLOCKED
from constants import REGION_SIZE


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
        tile_x, tile_y = get_tile_from_mouse(
            self.client.mouseWatcherNode,
            self.client.camera,
            self.client.render,
        )
        if tile_x is None:
            return
        rx, ry = world_to_region(tile_x, tile_y)
        region = self.world.region_manager.loaded.get((rx, ry))
        if region is None:
            self.world.region_manager.ensure(tile_x, tile_y)
            region = self.world.region_manager.loaded.get((rx, ry))
            if region is None:
                return
        lx, ly = local_tile(tile_x, tile_y)
        region.flags[ly, lx] ^= FLAG_BLOCKED
        region.make_mesh()
        if region.node is not None:
            parent = getattr(self.client, "tile_root", self.client.render)
            region.node.reparentTo(parent)
            region.node.setPos(
                region.rx * REGION_SIZE,
                region.ry * REGION_SIZE,
                0,
            )

    def toggle_interactable(self):
        if self.client.options_menu.visible:
            return
        tile_x, tile_y = get_tile_from_mouse(
            self.client.mouseWatcherNode,
            self.client.camera,
            self.client.render,
        )
        if tile_x is None:
            return
        rx, ry = world_to_region(tile_x, tile_y)
        region = self.world.region_manager.loaded.get((rx, ry))
        if region is None:
            self.world.region_manager.ensure(tile_x, tile_y)
            region = self.world.region_manager.loaded.get((rx, ry))
            if region is None:
                return
        lx, ly = local_tile(tile_x, tile_y)
        region.overlay[ly, lx] ^= 1
        region.make_mesh()
        if region.node is not None:
            parent = getattr(self.client, "tile_root", self.client.render)
            region.node.reparentTo(parent)
            region.node.setPos(
                region.rx * REGION_SIZE,
                region.ry * REGION_SIZE,
                0,
            )

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------
    def save_map(self):
        """Save all loaded regions to disk."""
        for region in self.world.region_manager.loaded.values():
            region.save()

    def load_map(self):
        """Load map data by clearing and reloading regions from disk."""
        self.world.region_manager.loaded.clear()
        self.world.region_manager.ensure(0, 0)

    # ------------------------------------------------------------------
    # Hotkeys used when running the editor standalone
    # ------------------------------------------------------------------
    def _hotkey_save(self):
        if hasattr(self, "save_callback"):
            self.save_callback()
        else:
            try:
                self.save_map()
                print("Map saved to map.json")
            except Exception as exc:
                print(f"Failed to save map: {exc}")

    def _hotkey_load(self):
        if hasattr(self, "load_callback"):
            self.load_callback()
        else:
            try:
                self.load_map()
                print("Map loaded from map.json")
            except Exception as exc:
                print(f"Failed to load map: {exc}")
