from panda3d.core import NodePath
from runepy.controls import Controls

class CamControl:
    def __init__(self, camera):
        self.camera = camera


class FakeBase:
    def __init__(self, render):
        self.render = render
    def accept(self, *a, **k):
        pass


def test_zoom_clamp():
    render = NodePath('render')
    cam = NodePath('cam')
    cam.reparentTo(render)
    cam.setP(-90)
    cam.setPos(0, 0, 10)

    base = FakeBase(render)
    controls = Controls(base, CamControl(cam), None)

    controls.zoom(-1)
    assert cam.getZ() == 5.0

    cam.setZ(75)
    controls.zoom(1)
    assert cam.getZ() == 80.0
