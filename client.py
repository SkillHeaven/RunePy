from panda3d.core import ModifierButtons, Vec3
from direct.showbase.ShowBase import ShowBase
from direct.interval.IntervalGlobal import Sequence, Func
import math
import argparse

from Character import Character
from DebugInfo import DebugInfo
from Camera import CameraControl
from Controls import Controls
from world import World
from pathfinding import a_star
from collision import CollisionControl
from map_editor import MapEditor


class Client(ShowBase):
    """Application entry point that opens the game window."""

    def __init__(self, debug=False):
        super().__init__()
        self.debug = debug
        self.disableMouse()
        self.debug_info = DebugInfo()

        self.mouseWatcherNode.set_modifier_buttons(ModifierButtons())
        self.buttonThrowers[0].node().set_modifier_buttons(ModifierButtons())

        self.world = World(self.render, debug=debug)
        self.grid = self.world.grid
        self.map_radius = self.world.radius

        tile_fit_scale = self.world.tile_size * 0.5
        self.character = Character(self.render, self.loader, Vec3(0, 0, 0.5), scale=tile_fit_scale, debug=debug)
        self.camera_control = CameraControl(self.camera, self.render, self.character)
        self.controls = Controls(self, self.camera_control, self.character)
        self.collision_control = CollisionControl(self.camera, self.render)
        self.editor = MapEditor(self, self.world)
        self.editor.save_callback = self.save_map
        self.editor.load_callback = self.load_map

        self.accept("mouse1", self.tile_click_event)

        self.setBackgroundColor(0.5, 0.5, 0.5)
        self.camera.setPos(0, 0, 10)
        self.camera.lookAt(0, 0, 0)

        self.taskMgr.add(self.update_tile_hover, "updateTileHoverTask")

    def log(self, *args, **kwargs):
        if self.debug:
            print(*args, **kwargs)

    def get_mouse_tile_coords(self):
        if self.mouseWatcherNode.hasMouse():
            mpos = self.mouseWatcherNode.getMouse()
            tile_x = round(mpos.getX() * 10)
            tile_y = round(mpos.getY() * 10)
            return mpos, tile_x, tile_y
        return None, None, None

    def get_tile_from_mouse(self):
        _, tile_x, tile_y = self.get_mouse_tile_coords()
        return tile_x, tile_y

    def update_tile_hover(self, task):
        mpos, tile_x, tile_y = self.get_mouse_tile_coords()
        if mpos:
            self.debug_info.update_tile_info(mpos, tile_x, tile_y)
        return task.cont

    def tile_click_event(self):
        self.log("Tile clicked!")
        if self.mouseWatcherNode.hasMouse():
            mpos = self.mouseWatcherNode.getMouse()
            self.log(f"Mouse position detected: {mpos}")
        else:
            self.log("No mouse detected.")
            return

        self.camera.setH(0)
        self.collision_control.update_ray(self.camNode, mpos)
        self.log("Before traversing for collisions...")
        self.collision_control.traverser.traverse(self.render)
        self.log("After traversing for collisions.")

        collided_obj, pickedPos = self.collision_control.get_collided_object(self.render)

        if collided_obj:
            self.log("Collided with:", collided_obj.getName())

            snapped_x = round(pickedPos.getX())
            snapped_y = round(pickedPos.getY())
            target_pos = Vec3(snapped_x, snapped_y, 0.5)

            if (self.character.get_position() - target_pos).length() > 0.1:
                # Stop any ongoing movement so the path starts from the exact current position
                self.character.cancel_movement()
                current_pos = self.character.get_position()
                current_x, current_y = int(current_pos.getX()), int(current_pos.getY())

                start_idx = (current_x + self.map_radius, current_y + self.map_radius)
                end_idx = (snapped_x + self.map_radius, snapped_y + self.map_radius)

                path = a_star(self.grid, start_idx, end_idx)
                self.log("Calculated Path:", path)

                if path:
                    # Skip the starting tile so movement begins from the
                    # character's actual position without resetting to the
                    # rounded tile coordinate.
                    if path and path[0] == start_idx:
                        path = path[1:]

                    if not path:
                        self.log("Already at destination")
                        return

                    intervals = []
                    prev_world_x, prev_world_y = current_pos.getX(), current_pos.getY()
                    for step in path:
                        world_x = step[0] - self.map_radius
                        world_y = step[1] - self.map_radius
                        self.log(f"Moving character to {(world_x, world_y)}")
                        distance = math.sqrt((world_x - prev_world_x) ** 2 + (world_y - prev_world_y) ** 2)
                        duration = distance / self.character.speed
                        move_interval = self.character.move_to(Vec3(world_x, world_y, 0.5), duration)
                        intervals.append(move_interval)
                        prev_world_x, prev_world_y = world_x, world_y

                    move_sequence = Sequence(*intervals, Func(self.camera_control.update_camera_focus))
                    self.character.start_sequence(move_sequence)
                    self.log(f"Moved to {(world_x, world_y)}")

                self.log(f"After Update: Camera Hpr: {self.camera.getHpr()}")
                self.log(f"After Update: Character Pos: {self.character.get_position()}")

        self.collision_control.cleanup()

    # ------------------------------------------------------------------
    # Editor helpers
    # ------------------------------------------------------------------
    def save_map(self, filename="map.json"):
        """Save the current world grid to ``filename``."""
        self.editor.save_map(filename)
        print(f"Map saved to {filename}")

    def load_map(self, filename="map.json"):
        """Load a map from ``filename`` and rebuild the world."""
        self.editor.load_map(filename)
        print(f"Map loaded from {filename}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RunePy client")
    parser.add_argument(
        "--mode",
        choices=["game", "editor"],
        default="game",
        help="Start in regular game mode or map editor",
    )
    args = parser.parse_args()

    if args.mode == "editor":
        from editor_window import EditorWindow

        app = EditorWindow()
    else:
        app = Client()
    app.run()
