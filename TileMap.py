#TileMap.py
from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
import random
from direct.interval.IntervalGlobal import Sequence, Func

from panda3d.core import CollisionRay

from Character import Character
from DebugInfo import DebugInfo
from Camera import CameraControl
from Controls import Controls
from pathfinding import a_star
from collision import CollisionControl


class TileMap(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.disableMouse()
        self.debug_info = DebugInfo()
        tile_size = 1
        map_radius = 5  # Number of tiles from the center to the edge, not including center
        map_width = map_height = map_radius * 2 + 1
        self.tiles = []
        self.grid = [[1 for _ in range(map_width)] for _ in range(map_height)]

        self.mouseWatcherNode.set_modifier_buttons(ModifierButtons())
        self.buttonThrowers[0].node().set_modifier_buttons(ModifierButtons())

        tile_fit_scale = tile_size * 0.5  # Scale the model to 50% of the tile size for some padding
        self.character = Character(self.render, self.loader, Vec3(0, 0, 0.5), scale=tile_fit_scale)
        self.camera_control = CameraControl(self.camera, self.render, self.character)
        self.controls = Controls(self, self.camera_control, self.character)
        self.collision_control = CollisionControl(self.camera, self.render)



        for x in range(-map_radius, map_radius + 1):  # will loop from -5 to 5
            for y in range(-map_radius, map_radius + 1):
                tile = self.create_tile((x * tile_size, y * tile_size, 0), tile_size)
                random_color = (random.random(), random.random(), random.random(), 1)
                tile.setColor(random_color)
                tile.setName(f"tile_{x}_{y}")


        self.accept('mouse1', self.tile_click_event)

        self.setBackgroundColor(0.5, 0.5, 0.5)
        self.camera.setPos(0,0,10)
        self.camera.lookAt(0,0,0)

        # self.taskMgr.add(self.controls.middle_mouse_drag_event, 'middleMouseTask')

        self.taskMgr.add(self.update_tile_hover, 'updateTileHoverTask')

    def create_tile(self, position, size):
        card_maker = CardMaker("tile")
        card_maker.setFrame(-size / 2, size / 2, -size / 2, size / 2)  # size of the card
        tile = self.render.attachNewNode(card_maker.generate())
        tile.setPos(*position)
        tile.setHpr(0, -90, 0)

        # Create a collision solid for this tile
        c_node = CollisionNode(f"coll_tile_{position[0]}_{position[1]}")
        c_node.addSolid(CollisionPolygon(Point3(-size / 2, -size / 2, 0),
                                         Point3(size / 2, -size / 2, 0),
                                         Point3(size / 2, size / 2, 0),
                                         Point3(-size / 2, size / 2, 0)))
        tile.attachNewNode(c_node)
        c_node.set_into_collide_mask(BitMask32.all_on())

        return tile

    def get_mouse_tile_coords(self):
        if self.mouseWatcherNode.hasMouse():
            mpos = self.mouseWatcherNode.getMouse()
            tile_x = round(mpos.getX() * 10)
            tile_y = round(mpos.getY() * 10)
            return mpos, tile_x, tile_y
        return None, None, None


    def get_tile_from_mouse(self):
        if self.mouseWatcherNode.hasMouse():
            mpos = self.mouseWatcherNode.getMouse()
            tile_x = round(mpos.getX() * 10)
            tile_y = round(mpos.getY() * 10)
            return tile_x, tile_y
        return None, None

    def update_tile_hover(self, task):
        mpos, tile_x, tile_y = self.get_mouse_tile_coords()
        if mpos:
            self.debug_info.update_tile_info(mpos, tile_x, tile_y)

        return task.cont

    def tile_click_event(self):
        print("Tile clicked!")
        if self.mouseWatcherNode.hasMouse():
            mpos = self.mouseWatcherNode.getMouse()
            print(f"Mouse position detected: {mpos}")
        else:
            print("No mouse detected.")
            return

        self.camera.setH(0)

        # Update ray with current mouse position
        self.collision_control.update_ray(self.camNode, mpos)
        print("Before traversing for collisions...")
        self.collision_control.traverser.traverse(self.render)
        print("After traversing for collisions.")

        collided_obj, pickedPos = self.collision_control.get_collided_object(self.render)

        if collided_obj:
            print("Collided with:", collided_obj.getName())

            snapped_x = round(pickedPos.getX())
            snapped_y = round(pickedPos.getY())
            targetPos = Vec3(snapped_x, snapped_y, 0.5)

            if (self.character.get_position() - targetPos).length() > 0.1:
                current_pos = self.character.get_position()
                current_x, current_y = int(current_pos.getX()), int(current_pos.getY())

                path = a_star(self.grid, (current_x, current_y), (snapped_x, snapped_y))
                print("Calculated Path:", path)

                if path:
                    intervals = []
                    for step in path:
                        print(f"Moving character to {step}")
                        move_interval = self.character.move_to(Vec3(step[0], step[1], 0.5))
                        intervals.append(move_interval)

                    move_sequence = Sequence(*intervals, Func(self.camera_control.update_camera_focus))
                    move_sequence.start()
                    print(f"Moved to {step}")

                print(f"After Update: Camera Hpr: {self.camera.getHpr()}")
                print(f"After Update: Character Pos: {self.character.get_position()}")

        self.collision_control.cleanup()



if __name__ == "__main__":
    app = TileMap()
    app.run()
