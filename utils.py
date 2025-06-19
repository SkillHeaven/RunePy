# Utility functions shared across modules
from panda3d.core import MouseWatcher


def get_mouse_tile_coords(mouse_watcher: "MouseWatcher"):
    """Return the mouse position and snapped tile coordinates."""
    if mouse_watcher and mouse_watcher.hasMouse():
        mpos = mouse_watcher.getMouse()
        tile_x = round(mpos.getX() * 10)
        tile_y = round(mpos.getY() * 10)
        return mpos, tile_x, tile_y
    return None, None, None


def get_tile_from_mouse(mouse_watcher: "MouseWatcher"):
    """Return just the tile coordinates from the mouse position."""
    _, tile_x, tile_y = get_mouse_tile_coords(mouse_watcher)
    return tile_x, tile_y
