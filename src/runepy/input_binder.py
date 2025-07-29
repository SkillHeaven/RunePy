import logging
from runepy.options_menu import KeyBindingManager, OptionsMenu


logger = logging.getLogger(__name__)


class InputBinder:
    """Bind mouse and keyboard events for the client."""

    def __init__(self, base, pathfinder, debug_info, key_bindings=None):
        self.base = base
        self.pathfinder = pathfinder
        self.debug_info = debug_info

        self.key_manager = KeyBindingManager(base, key_bindings or {"open_menu": "escape"})
        self.options_menu = OptionsMenu(base, self.key_manager)
        base.key_manager = self.key_manager
        base.options_menu = self.options_menu
        self.key_manager.bind("open_menu", self.options_menu.toggle)

        self.tile_click_event_ref = self.on_click
        base.tile_click_event_ref = self.on_click
        base.accept("mouse1", self.tile_click_event_ref)
        if self.debug_info is not None:
            base.accept("f3", self.debug_info.toggle_region_info)

    def on_click(self):
        if self.options_menu.visible:
            return
        if not self.base.mouseWatcherNode.hasMouse():
            return
        mpos = self.base.mouseWatcherNode.getMouse()
        self.base.camera.setH(0)
        self.base.collision_control.update_ray(self.base.camNode, mpos)
        self.base.collision_control.traverser.traverse(self.base.render)
        collided_obj, pickedPos = self.base.collision_control.get_collided_object(self.base.render)
        if collided_obj:
            snapped_x = round(pickedPos.getX())
            snapped_y = round(pickedPos.getY())
            self.pathfinder.move_along_path(snapped_x, snapped_y)
        self.base.collision_control.cleanup()

