from direct.showbase.ShowBase import ShowBase
from world import World
from map_editor import MapEditor


class EditorWindow(ShowBase):
    """Standalone application providing a minimal tile editor."""

    def __init__(self):
        super().__init__()
        self.disableMouse()

        self.world = World(self.render)
        self.editor = MapEditor(self, self.world)

        self.accept("escape", self.userExit)
        self.accept("s", self.save_map)
        self.accept("l", self.load_map)

        self.setBackgroundColor(0.5, 0.5, 0.5)
        self.camera.setPos(0, 0, 10)
        self.camera.lookAt(0, 0, 0)

    def save_map(self):
        self.editor.save_map("map.json")
        print("Map saved to map.json")

    def load_map(self):
        self.editor.load_map("map.json")
        print("Map loaded from map.json")


if __name__ == "__main__":
    app = EditorWindow()
    app.run()
