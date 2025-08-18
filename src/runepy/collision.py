# collision.py
from panda3d.core import (
    BitMask32,
    CollisionHandlerQueue,
    CollisionNode,
    CollisionRay,
    CollisionTraverser,
)


class CollisionControl:
    def __init__(self, camera, render):
        self.camera = camera
        self.render = render
        self.traverser = CollisionTraverser()
        self.handler = CollisionHandlerQueue()

        # Initialize pickerRay and pickerNP
        self.pickerRay = CollisionRay()
        self.pickerNP = self.camera.attachNewNode(CollisionNode('mouseRay'))
        self.pickerNP.node().addSolid(self.pickerRay)
        self.pickerNP.node().setFromCollideMask(BitMask32.all_on())
        self.pickerNP.node().setIntoCollideMask(BitMask32.all_off())

        self.traverser.addCollider(self.pickerNP, self.handler)

    def update_ray(self, camNode, mpos):
        self.pickerRay.setFromLens(camNode, mpos.getX(), mpos.getY())

    def traverser_ray(self, render):
        self.traverser.traverse(render)

    def get_collided_object(self, render):
        if self.handler.getNumEntries() > 0:
            self.handler.sortEntries()
            return (
                self.handler.getEntry(0).getIntoNodePath(),
                self.handler.getEntry(0).getSurfacePoint(render),
            )
        else:
            return None, None

    def cleanup(self):
        """Reset the collision handler for the next ray cast without removing
        the collision node itself."""
        self.handler.clearEntries()
