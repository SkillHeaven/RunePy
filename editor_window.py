from direct.showbase.ShowBase import ShowBase
from world import World
from map_editor import MapEditor
from Camera import FreeCameraControl
from options_menu import KeyBindingManager, OptionsMenu



class EditorWindow(ShowBase):
    """Standalone application providing a minimal tile editor."""

    def __init__(self):
        super().__init__()
        self.disableMouse()

        self.world = World(self.render)
        self.editor = MapEditor(self, self.world)
        self.editor.save_callback = self.save_map
        self.editor.load_callback = self.load_map

        self.camera_control = FreeCameraControl(self.camera)
        self.camera_control.start(self)

        default_keys = {
            "open_menu": "escape",
            "save_map": "control-s",
            "load_map": "control-l",
            "toggle_tile": "mouse3",
            "toggle_interactable": "i",
            "move_forward": "w",
            "move_back": "s",
            "move_left": "a",
            "move_right": "d",
        }
        self.key_manager = KeyBindingManager(self, default_keys)
        self.options_menu = OptionsMenu(self, self.key_manager)

        self.key_manager.bind("open_menu", self.options_menu.toggle)
        self.editor.register_bindings(self.key_manager)
        self.key_manager.bind("move_forward",
                              lambda: self.camera_control.set_move("forward", True),
                              lambda: self.camera_control.set_move("forward", False))
        self.key_manager.bind("move_back",
                              lambda: self.camera_control.set_move("back", True),
                              lambda: self.camera_control.set_move("back", False))
        self.key_manager.bind("move_left",
                              lambda: self.camera_control.set_move("left", True),
                              lambda: self.camera_control.set_move("left", False))
        self.key_manager.bind("move_right",
                              lambda: self.camera_control.set_move("right", True),
                              lambda: self.camera_control.set_move("right", False))

        self.setBackgroundColor(0.9, 0.9, 0.9)

        self.camera.setPos(0, 0, 10)
        self.camera.lookAt(0, 0, 0)

    def get_mouse_tile_coords(self):
        """Return the mouse position and snapped tile coordinates."""
        if self.mouseWatcherNode.hasMouse():
            mpos = self.mouseWatcherNode.getMouse()
            tile_x = round(mpos.getX() * 10)
            tile_y = round(mpos.getY() * 10)
            return mpos, tile_x, tile_y
        return None, None, None

    def get_tile_from_mouse(self):
        """Return just the tile coordinates from the mouse position."""
        _, tile_x, tile_y = self.get_mouse_tile_coords()
        return tile_x, tile_y

    def save_map(self):
        self.editor.save_map("map.json")
        print("Map saved to map.json")

    def load_map(self):
        self.editor.load_map("map.json")
        print("Map loaded from map.json")


if __name__ == "__main__":
    app = EditorWindow()
    app.run()
