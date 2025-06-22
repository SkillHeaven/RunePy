from runepy.base_app import BaseApp
from runepy.world import World
from runepy.map_editor import MapEditor
from runepy.camera import FreeCameraControl
from runepy.options_menu import KeyBindingManager, OptionsMenu
from runepy.controls import Controls
from runepy.utils import get_mouse_tile_coords, get_tile_from_mouse



class EditorWindow(BaseApp):
    """Standalone application providing a minimal tile editor."""

    def __init__(self):
        super().__init__()

    def initialize(self):
        self.world = World(self.render)
        self.editor = MapEditor(self, self.world)
        self.editor.save_callback = self.save_map
        self.editor.load_callback = self.load_map

        self.camera_control = FreeCameraControl(self.camera)
        self.camera_control.start(self)
        self.controls = Controls(self, self.camera_control, None)

        default_keys = {
            "open_menu": "escape",
            "save_map": "control-s",
            "load_map": "control-l",
            "toggle_tile": "mouse3",
            "toggle_interactable": "i",
            "move_left": "a",
            "move_right": "d",
        }
        self.key_manager = KeyBindingManager(self, default_keys)
        self.options_menu = OptionsMenu(self, self.key_manager)

        self.key_manager.bind("open_menu", self.options_menu.toggle)
        self.editor.register_bindings(self.key_manager)
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
        self.accept("w-up", lambda: self.camera_control.set_move("forward", False))
        self.accept("s", lambda: self.camera_control.set_move("back", True))
        self.accept("s-up", lambda: self.camera_control.set_move("back", False))

        # Editor uses the same sky blue background as the game
        self.setBackgroundColor(0.53, 0.81, 0.92)

        self.camera.setPos(0, 0, 10)
        self.camera.lookAt(0, 0, 0)

        self.taskMgr.add(self.update_tile_hover, "updateTileHoverTask")

    def update_tile_hover(self, task):
        mpos, tile_x, tile_y = get_mouse_tile_coords(
            self.mouseWatcherNode, self.camera, self.render
        )
        if mpos:
            if -self.world.radius <= tile_x <= self.world.radius and -self.world.radius <= tile_y <= self.world.radius:
                self.world.highlight_tile(tile_x, tile_y)
            else:
                self.world.clear_highlight()
        else:
            self.world.clear_highlight()
        return task.cont

    def save_map(self):
        self.editor.save_map("map.json")
        print("Map saved to map.json")

    def load_map(self):
        self.editor.load_map("map.json")
        print("Map loaded from map.json")


if __name__ == "__main__":
    app = EditorWindow()
    app.run()
