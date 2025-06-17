#Controls.py
from direct.showbase.DirectObject import DirectObject
from panda3d.core import Vec3

class Controls(DirectObject):

    def __init__(self, base, camera, character):
        self.base = base
        self.camera_control = camera

        #self.middle_mouse_down = False

        self.accept("wheel_up", self.zoom, [-1])
        self.accept("wheel_down", self.zoom, [1])
        # self.accept('mouse3', self.middle_mouse_down_event)
        # self.accept('mouse3-up', self.middle_mouse_up_event)
        # self.base.taskMgr.add(self.middle_mouse_drag_event, 'middleMouseTask')

    def zoom(self, direction):
        zoom_speed = 10
        cam_vec = self.base.render.getRelativeVector(self.camera_control.camera, Vec3(0, 1, 0))
        self.camera_control.camera.setPos(self.camera_control.camera.getPos() - cam_vec * direction * zoom_speed)

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
    #         self.camera.setH(self.camera.getH() - delta_x * 100)  # Adjust sensitivity as needed
    #         self.last_mouse_pos = current_mouse_pos
    #     return task.cont
