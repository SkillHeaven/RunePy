import logging
from panda3d.core import ModifierButtons, Vec3
try:
    import direct.showbase.ShowBaseGlobal as sbg
except Exception:  # pragma: no cover - Panda3D may be missing
    sbg = None
from runepy.utils import update_tile_hover as util_update_tile_hover
import argparse
from runepy import verbose

logger = logging.getLogger(__name__)

from runepy.base_app import BaseApp

from runepy.character import Character
from runepy.debuginfo import DebugInfo
from runepy.camera import CameraControl
from runepy.controls import Controls
from runepy.world.world import World
from constants import REGION_SIZE, VIEW_RADIUS
from runepy.pathfinding import Pathfinder
from runepy.input_binder import InputBinder
from runepy.collision import CollisionControl
from runepy.config import load_state, save_state
import atexit


class Client(BaseApp):
    """Application entry point that opens the game window."""

    def __init__(self, debug=False):
        self.debug = debug
        super().__init__()
        atexit.register(self._save_state)

    def initialize(self):
        """Perform heavy initialization for the game mode."""
        self.debug_info = DebugInfo()

        self.mouseWatcherNode.set_modifier_buttons(ModifierButtons())
        self.buttonThrowers[0].node().set_modifier_buttons(ModifierButtons())

        self.loading_screen.update(20, "Generating world")

        def world_progress(frac, text):
            self.loading_screen.update(20 + int(30 * frac), text)

        view_radius = VIEW_RADIUS
        world_radius = view_radius * REGION_SIZE
        self.world = World(
            self.render,
            radius=world_radius,
            debug=self.debug,
            progress_callback=world_progress,
            view_radius=view_radius,
        )

        tile_fit_scale = self.world.tile_size * 0.5
        self.loading_screen.update(50, "Loading character")
        self.character = Character(
            self.render,
            self.loader,
            Vec3(0, 0, 0.5),
            scale=tile_fit_scale,
            debug=self.debug,
        )
        if sbg is not None and hasattr(sbg, "base"):
            sbg.base.world = self.world
            sbg.base.character = self.character
        self.camera_control = CameraControl(
            self.camera,
            self.render,
            self.character,
        )
        state = load_state()
        char_pos = state.get("character_pos")
        if isinstance(char_pos, list) and len(char_pos) == 3:
            self.character.model.setPos(*char_pos)
        cam_h = state.get("camera_height")
        if cam_h is not None:
            self.camera.setZ(cam_h)
            self.camera_control.update_camera_focus()
        self.controls = Controls(self, self.camera_control, self.character)
        self.collision_control = CollisionControl(self.camera, self.render)
        self.pathfinder = Pathfinder(self.character, self.world, self.camera_control, debug=self.debug)
        self.input_binder = InputBinder(self, self.pathfinder, self.debug_info)

        self.loading_screen.update(80, "Finalizing")
        # Set a pleasant sky blue background
        self.setBackgroundColor(0.53, 0.81, 0.92)
        if cam_h is None:
            self.camera.setPos(0, 0, 10)
        self.camera.lookAt(0, 0, 0)

        self.taskMgr.add(self.update_tile_hover, "updateTileHoverTask")

    def log(self, *args, **kwargs):
        if self.debug:
            logger.debug(*args, **kwargs)

    def update_tile_hover(self, task):
        util_update_tile_hover(
            self.mouseWatcherNode,
            self.camera,
            self.render,
            self.world,
            debug=self.debug_info,
        )
        return task.cont

    def tile_click_event(self):
        self.input_binder.on_click()
    # Editor helpers
    # ------------------------------------------------------------------
    def save_map(self, filename="map.json"):
        """Save the current world grid to ``filename``."""
        self.editor.save_map()
        logger.info(f"Map saved to {filename}")

    def load_map(self, filename="map.json"):
        """Load a map from ``filename`` and rebuild the world."""
        self.editor.load_map()
        # World size may change during map load but pathfinding now stitches
        # regions dynamically so no cached grid is needed.
        logger.info(f"Map loaded from {filename}")

    # ------------------------------------------------------------------
    # State persistence
    # ------------------------------------------------------------------
    def _save_state(self):
        """Save camera height and character position."""
        if not hasattr(self, "character"):
            return
        state = {
            "camera_height": float(self.camera.getZ()),
            "character_pos": [
                float(self.character.model.getX()),
                float(self.character.model.getY()),
                float(self.character.model.getZ()),
            ],
        }
        save_state(state)


def main(args=None):
    """Entry point for the ``runepy`` console script."""
    parser = argparse.ArgumentParser(description="RunePy client")
    parser.add_argument(
        "--mode",
        choices=["game", "editor"],
        default="game",
        help="Start in regular game mode or map editor",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging of all function calls",
    )
    parsed = parser.parse_args(args)

    if parsed.verbose:
        verbose.enable()

    if parsed.mode == "editor":
        from runepy.editor_window import EditorWindow

        app = EditorWindow()
    else:
        app = Client()

    from runepy.debug import get_debug
    get_debug().attach(app)

    app.run()


if __name__ == "__main__":
    main()

__all__ = ["Client", "main"]
