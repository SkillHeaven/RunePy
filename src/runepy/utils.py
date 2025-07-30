# Utility functions shared across modules
from panda3d.core import MouseWatcher, Plane, Point3, Vec3
import math
from contextlib import contextmanager


def get_mouse_tile_coords(
    mouse_watcher: "MouseWatcher",
    camera,
    render,
) -> tuple:
    """Return the mouse position and world tile coordinates.

    ``camera`` and ``render`` should be the current camera node and the
    render root so the mouse ray can be projected into world space.
    """
    if mouse_watcher and mouse_watcher.hasMouse():
        if not camera or not render:
            return None, None, None
        mpos = mouse_watcher.getMouse()
        node = camera.node()
        if hasattr(node, "getLens"):
            lens = node.getLens()
        else:
            cam = camera.find("**/+Camera")
            if cam.isEmpty():
                return None, None, None
            lens = cam.node().getLens()
        near = Point3()
        far = Point3()
        lens.extrude(mpos, near, far)
        near_world = render.getRelativePoint(camera, near)
        far_world = render.getRelativePoint(camera, far)
        plane = Plane(Vec3(0, 0, 1), Point3(0, 0, 0))
        intersection = Point3()
        if plane.intersectsLine(intersection, near_world, far_world):
            tile_x = math.floor(intersection.getX())
            tile_y = math.floor(intersection.getY())
            return mpos, tile_x, tile_y
    return None, None, None


def get_tile_from_mouse(mouse_watcher: "MouseWatcher", camera, render):
    """Return just the tile coordinates from the mouse position."""
    _, tile_x, tile_y = get_mouse_tile_coords(mouse_watcher, camera, render)
    return tile_x, tile_y

def update_tile_hover(
    mouse_watcher: "MouseWatcher",
    camera,
    render,
    world,
    debug=None,
) -> tuple:
    """Highlight the tile under the mouse and optionally update debug info."""

    mpos, tile_x, tile_y = get_mouse_tile_coords(mouse_watcher, camera, render)

    if mpos:
        if debug is not None:
            debug.update_tile_info(mpos, tile_x, tile_y)

        if (
            -world.radius <= tile_x <= world.radius
            and -world.radius <= tile_y <= world.radius
        ):
            world.highlight_tile(tile_x, tile_y)
        else:
            world.clear_highlight()
    else:
        world.clear_highlight()

    return mpos, tile_x, tile_y


@contextmanager
def suspend_mouse_click(base):
    """Temporarily disable the base ``mouse1`` handler."""

    handler = None
    if base is not None:
        handler = getattr(base, "tile_click_event_ref", None)
        if handler is None:
            handler = getattr(base, "tile_click_event", None)
        if handler is not None:
            try:
                base.ignore("mouse1")
            except Exception:  # pragma: no cover - ignore failures
                handler = None
    try:
        yield
    finally:
        if base is not None and handler is not None:
            try:
                base.accept("mouse1", handler)
            except Exception:  # pragma: no cover - ignore failures
                pass
