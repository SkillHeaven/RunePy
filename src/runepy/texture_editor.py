from __future__ import annotations

"""Simple per-tile texture editor."""

try:
    from direct.gui.DirectGui import DirectFrame, DirectButton
except Exception:  # pragma: no cover - Panda3D may be missing
    DirectFrame = object  # type: ignore
    DirectButton = object  # type: ignore

from runepy.ui.common import create_ui
from runepy.ui.layouts import TEXTURE_EDITOR_LAYOUT
from typing import Any

from constants import REGION_SIZE
from runepy.world.region import world_to_region, local_tile


class TextureEditor:
    """Lightweight tool for editing per-tile textures."""

    def __init__(self, base: Any, world) -> None:
        self.base = base
        self.world = world
        self.selected_color = 0
        self.region = None
        self.lx = None
        self.ly = None
        self._click_ctx = None
        self.frame, widgets = create_ui(TEXTURE_EDITOR_LAYOUT, self)
        if hasattr(self.frame, "hide"):
            self.frame.hide()
        self._grid_buttons = [[widgets.get(f"cell_{x}_{y}") for x in range(16)] for y in range(16)]
        for i, val in enumerate([0, 64, 128, 192, 255]):
            btn = widgets.get(f"palette_{i}")
            if btn is not None and hasattr(btn, "__setitem__"):
                btn["command"] = lambda v=val: self.set_color(v)
        for y in range(16):
            for x in range(16):
                btn = widgets.get(f"cell_{x}_{y}")
                if btn is not None and hasattr(btn, "__setitem__"):
                    btn["command"] = lambda xx=x, yy=y: self.paint(xx, yy)
        close_btn = widgets.get("close_btn")
        if close_btn is not None and hasattr(close_btn, "__setitem__"):
            close_btn["command"] = self.close

    # ------------------------------------------------------------------
    def open(self, tile_x: int, tile_y: int) -> None:
        """Open the editor for the given tile."""
        from runepy.utils import suspend_mouse_click
        if self._click_ctx is None:
            self._click_ctx = suspend_mouse_click(self.base)
            self._click_ctx.__enter__()
        rx, ry = world_to_region(tile_x, tile_y)
        region = self.world.region_manager.loaded.get((rx, ry))
        if region is None:
            self.world.region_manager.ensure(tile_x, tile_y)
            region = self.world.region_manager.loaded.get((rx, ry))
            if region is None:
                return
        lx, ly = local_tile(tile_x, tile_y)
        self.region = region
        self.lx = lx
        self.ly = ly
        if self.frame is not None:
            for y in range(16):
                for x in range(16):
                    val = int(region.textures[ly, lx, y, x])
                    btn = self._grid_buttons[y][x]
                    if btn is not None and hasattr(btn, '__setitem__'):
                        btn['text'] = ''
                        btn['frameColor'] = (val / 255.0,) * 3 + (1,)
            self.frame.show()

    def close(self) -> None:
        if self.frame is not None:
            self.frame.hide()
        if self._click_ctx is not None:
            self._click_ctx.__exit__(None, None, None)
            self._click_ctx = None
        self.region = None
        self.lx = None
        self.ly = None

    # ------------------------------------------------------------------
    def set_color(self, val: int) -> None:
        self.selected_color = max(0, min(255, int(val)))

    def paint(self, px: int, py: int) -> None:
        if self.region is None:
            return
        self.region.textures[self.ly, self.lx, py, px] = self.selected_color
        if self.frame is not None:
            btn = self._grid_buttons[py][px]
            if btn is not None and hasattr(btn, '__setitem__'):
                btn['frameColor'] = (self.selected_color / 255.0,) * 3 + (1,)
        self.region.make_mesh()
        if self.region.node is not None and hasattr(self.base, 'render'):
            parent = getattr(self.base, 'tile_root', self.base.render)
            self.region.node.reparentTo(parent)
            self.region.node.setPos(
                self.region.rx * REGION_SIZE,
                self.region.ry * REGION_SIZE,
                0,
            )
