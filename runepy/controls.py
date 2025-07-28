# Controls.py
from direct.showbase.DirectObject import DirectObject
from panda3d.core import Vec3


class Controls(DirectObject):

    def __init__(self, base, camera, character):
        self.base = base
        self.camera_control = camera

        # self.middle_mouse_down = False

        self.accept("wheel_up", self.zoom, [-1])
        self.accept("wheel_down", self.zoom, [1])
        # self.accept('mouse3', self.middle_mouse_down_event)
        # self.accept('mouse3-up', self.middle_mouse_up_event)
        # self.base.taskMgr.add(
        #     self.middle_mouse_drag_event,
        #     'middleMouseTask',
        # )

    def zoom(self, direction):
        """Zoom the camera while clamping the minimum and maximum height."""
        zoom_speed = 10
        cam_vec = self.base.render.getRelativeVector(
            self.camera_control.camera, Vec3(0, 1, 0)
        )

        # Calculate the camera's new position in world space
        current_world_pos = self.camera_control.camera.getPos(self.base.render)
        new_world_pos = current_world_pos - cam_vec * direction * zoom_speed

        # Prevent the camera from moving below or far above the map plane
        min_z = 5.0
        max_z = 80.0
        if new_world_pos.getZ() < min_z:
            new_world_pos.setZ(min_z)
        elif new_world_pos.getZ() > max_z:
            new_world_pos.setZ(max_z)

        # Convert back to the camera's parent space before applying
        parent = self.camera_control.camera.getParent()
        new_local_pos = parent.getRelativePoint(
            self.base.render,
            new_world_pos,
        )
        self.camera_control.camera.setPos(new_local_pos)

    # def middle_mouse_down_event(self):
    #     self.middle_mouse_down = True
    #     if self.mouseWatcherNode.hasMouse():
    #         self.last_mouse_pos = self.mouseWatcherNode.getMouse()
    #
    # def middle_mouse_up_event(self):
    #     self.middle_mouse_down = False
    #
    # def middle_mouse_drag_event(self, task):
    #     if not self.middle_mouse_down:
    #         return task.cont
    #     if self.mouseWatcherNode.hasMouse():
    #         current_mouse_pos = self.mouseWatcherNode.getMouse()
    #         delta_x = current_mouse_pos[0] - self.last_mouse_pos[0]
    #         self.camera.setH(
    #             self.camera.getH() - delta_x * 100
    #         )  # Adjust sensitivity as needed
    #         self.last_mouse_pos = current_mouse_pos
    #     return task.cont
