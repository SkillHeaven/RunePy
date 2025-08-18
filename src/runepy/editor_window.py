import logging

from constants import REGION_SIZE, VIEW_RADIUS
from runepy.base_app import BaseApp
from runepy.camera import FreeCameraControl
from runepy.controls import Controls
from runepy.debug import get_debug
from runepy.editor_toolbar import EditorToolbar
from runepy.map_editor import MapEditor
from runepy.options_menu import KeyBindingManager, OptionsMenu
from runepy.ui.editor import UIEditorController
from runepy.utils import update_tile_hover as util_update_tile_hover
from runepy.world.world import World

logger = logging.getLogger(__name__)



class EditorWindow(BaseApp):
    """Standalone application providing a minimal tile editor."""

    def __init__(self):
        super().__init__()

    def initialize(self):
        view_radius = VIEW_RADIUS
        world_radius = view_radius * REGION_SIZE
        self.world = World(
            self.render,
            radius=world_radius,
            view_radius=view_radius,
        )
        self.editor = MapEditor(self, self.world)
        self.editor.save_callback = self.save_map
        self.editor.load_callback = self.load_map

        self.camera_control = FreeCameraControl(self.camera, world=self.world)
        self.camera_control.start(self)
        self.controls = Controls(self, self.camera_control, None)

        default_keys = {
            "open_menu": "escape",
            "save_map": "control-s",
            "load_map": "control-l",
            "toggle_ui_editor": "control-e",
            "toggle_tile": "mouse3",
            "toggle_interactable": "i",
            "move_left": "a",
            "move_right": "d",
        }
        self.key_manager = KeyBindingManager(self, default_keys)
        self.options_menu = OptionsMenu(self, self.key_manager)

        self.key_manager.bind("open_menu", self.options_menu.toggle)
        self.key_manager.bind("toggle_ui_editor", self._toggle_ui_editor)
        self.editor.register_bindings(self.key_manager)
        self.toolbar = EditorToolbar(self, self.editor)
        toolbar_frame = getattr(self.toolbar, "frame", None)
        self.ui_editor = UIEditorController(toolbar_frame)
        self._ui_editor_enabled = False
        # Store the bound click handler so the texture editor can reliably
        # remove it without depending on ephemeral bound method objects.
        self.tile_click_event_ref = self.editor.handle_click
        self.accept("mouse1", self.tile_click_event_ref)
        self.key_manager.bind(
            "move_left",
            lambda: self.camera_control.set_move("left", True),
            lambda: self.camera_control.set_move("left", False),
        )
        self.key_manager.bind(
            "move_right",
            lambda: self.camera_control.set_move("right", True),
            lambda: self.camera_control.set_move("right", False),
        )

        # Bind forward/back movement directly so W/S are fixed keys
        self.accept("w", lambda: self.camera_control.set_move("forward", True))
        self.accept(
            "w-up",
            lambda: self.camera_control.set_move("forward", False),
        )
        self.accept("s", lambda: self.camera_control.set_move("back", True))
        self.accept(
            "s-up",
            lambda: self.camera_control.set_move("back", False),
        )

        # Editor uses the same sky blue background as the game
        self.setBackgroundColor(0.53, 0.81, 0.92)

        self.camera.setPos(0, 0, 10)
        self.camera.lookAt(0, 0, 0)

        self.taskMgr.add(self.update_tile_hover, "updateTileHoverTask")

    def update_tile_hover(self, task):
        util_update_tile_hover(
            self.mouseWatcherNode, self.camera, self.render, self.world
        )
        return task.cont

    def save_map(self):
        self.editor.save_map()
        logger.info("Map saved to map.json")

    def load_map(self):
        self.editor.load_map()
        logger.info("Map loaded from map.json")

    # ------------------------------------------------------------------
    def _toggle_ui_editor(self) -> None:
        if self._ui_editor_enabled:
            self.ui_editor.disable()
        else:
            self.ui_editor.enable()
        self._ui_editor_enabled = not self._ui_editor_enabled


if __name__ == "__main__":
    app = EditorWindow()
    get_debug().attach(app)
    app.run()
