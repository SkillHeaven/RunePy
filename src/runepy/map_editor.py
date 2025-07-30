import logging
from runepy.utils import get_tile_from_mouse
from runepy.world.region import world_to_region, local_tile
from runepy.terrain import FLAG_BLOCKED
from constants import REGION_SIZE
from runepy.texture_editor import TextureEditor

logger = logging.getLogger(__name__)


class MapEditor:
    """Basic tile editing functionality."""

    def __init__(self, client, world):
        self.client = client
        self.world = world
        self.mode = "tile"
        self.texture_editor = TextureEditor(client, world)

    def _get_mouse_tile(self):
        """Return the tile coordinates under the mouse or ``None``."""
        tile_x, tile_y = get_tile_from_mouse(
            self.client.mouseWatcherNode,
            self.client.camera,
            self.client.render,
        )
        if tile_x is None:
            return None
        return tile_x, tile_y

    def register_bindings(self, key_manager):
        """Register editor actions with ``key_manager``."""
        key_manager.bind("toggle_tile", self.toggle_tile)
        key_manager.bind("toggle_interactable", self.toggle_interactable)
        key_manager.bind("save_map", self._hotkey_save)
        key_manager.bind("load_map", self._hotkey_load)

    def set_mode(self, mode: str) -> None:
        self.mode = mode

    def handle_click(self) -> None:
        if self.mode == "tile":
            self.toggle_tile()
        elif self.mode == "interactable":
            self.toggle_interactable()


    def _toggle_region_value(self, tile_x: int, tile_y: int, array_name: str) -> None:
        """Toggle a value within a region array and refresh the mesh."""
        rx, ry = world_to_region(tile_x, tile_y)
        region = self.world.region_manager.loaded.get((rx, ry))
        if region is None:
            self.world.region_manager.ensure(tile_x, tile_y)
            region = self.world.region_manager.loaded.get((rx, ry))
            if region is None:
                return
        lx, ly = local_tile(tile_x, tile_y)
        array = getattr(region, array_name)
        array[ly, lx] ^= 1
        region.make_mesh()
        if region.node is not None:
            parent = getattr(self.client, "tile_root", self.client.render)
            region.node.reparentTo(parent)
            region.node.setPos(
                region.rx * REGION_SIZE,
                region.ry * REGION_SIZE,
                0,
            )

    def toggle_tile(self):
        if self.client.options_menu.visible:
            return
        pos = self._get_mouse_tile()
        if pos is None:
            return
        tile_x, tile_y = pos
        self._toggle_region_value(tile_x, tile_y, "flags")

    def toggle_interactable(self):
        if self.client.options_menu.visible:
            return
        pos = self._get_mouse_tile()
        if pos is None:
            return
        tile_x, tile_y = pos
        self._toggle_region_value(tile_x, tile_y, "overlay")
    def open_texture_editor(self):
        if self.client.options_menu.visible:
            return
        if self.texture_editor.region is not None:
            self.texture_editor.close()
            return
        pos = self._get_mouse_tile()
        if pos is None:
            return
        tile_x, tile_y = pos
        self.texture_editor.open(tile_x, tile_y)


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
                logger.info("Map saved to map.json")
            except Exception as exc:
                logger.exception("Failed to save map", exc_info=exc)

    def _hotkey_load(self):
        if hasattr(self, "load_callback"):
            self.load_callback()
        else:
            try:
                self.load_map()
                logger.info("Map loaded from map.json")
            except Exception as exc:
                logger.exception("Failed to load map", exc_info=exc)
