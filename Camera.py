from panda3d.core import Vec3
from Controls import Controls

class CameraControl:

    def __init__(self, camera, render, character):
        self.camera = camera
        self.render = render
        self.character = character


        self.last_mouse_pos = (0,0)

        self.camera.setPos(0,0,10)
        self.camera.reparentTo(self.character.model)
        self.update_camera_focus()

    def update_camera_focus(self):
        self.camera.setH(0)  # Reset heading
        self.camera.setP(-90)  # Set pitch to face downward
