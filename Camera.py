from panda3d.core import Vec3, ClockObject

# Initialize the global clock for time-based movement
globalClock = ClockObject.getGlobalClock()

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

class FreeCameraControl:
    """Camera controller allowing WASD movement for the editor."""

    def __init__(self, camera, speed=5.0):
        self.camera = camera
        self.speed = speed
        self.move = {"forward": False, "back": False, "left": False, "right": False}

    def start(self, base):
        self.base = base
        base.taskMgr.add(self.update, "freeCameraUpdate")

    def set_move(self, direction, value):
        self.move[direction] = value

    def update(self, task):
        dt = globalClock.getDt()
        vec = Vec3(0, 0, 0)
        if self.move["forward"]:
            vec.y += self.speed * dt
        if self.move["back"]:
            vec.y -= self.speed * dt
        if self.move["left"]:
            vec.x -= self.speed * dt
        if self.move["right"]:
            vec.x += self.speed * dt
        if vec.length_squared() > 0:
            # Move relative to the world axes to avoid changing height so
            # W/S pan the camera instead of zooming in and out.
            self.camera.setPos(
                self.camera.getX() + vec.x,
                self.camera.getY() + vec.y,
                self.camera.getZ(),
            )
        return task.cont

