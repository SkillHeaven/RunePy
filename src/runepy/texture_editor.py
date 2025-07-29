from __future__ import annotations

"""Simple per-tile texture editor."""

try:
    from direct.gui.DirectGui import DirectFrame, DirectButton
except Exception:  # pragma: no cover - Panda3D may be missing
    DirectFrame = object  # type: ignore
    DirectButton = object  # type: ignore

from typing import Any

from constants import REGION_SIZE
from runepy.world import world_to_region, local_tile


class TextureEditor:
    """Lightweight tool for editing per-tile textures."""

    def __init__(self, base: Any, world) -> None:
        self.base = base
        self.world = world
        self.frame = None
        self.selected_color = 0
        self.region = None
        self.lx = None
        self.ly = None
        self._orig_click_handler = None
        if DirectFrame is not object:
            self.frame = DirectFrame(
                frameColor=(0, 0, 0, 1),
                frameSize=(-0.6, 0.6, -0.6, 0.6),
                pos=(0, 0, 0.2),
            )
            self.frame.hide()
            palette = [0, 64, 128, 192, 255]
            step = 0.24
            for i, val in enumerate(palette):
                btn = DirectButton(
                    parent=self.frame,
                    text="",
                    frameColor=(val/255.0, val/255.0, val/255.0, 1),
                    scale=0.05,
                    pos=(-0.55 + i * step, 0, 0.45),
                    command=lambda v=val: self.set_color(v),
                )
            # 16x16 grid of buttons for painting
            self._grid_buttons = []
            gstep = 0.07
            start = -0.5
            for y in range(16):
                row = []
                for x in range(16):
                    btn = DirectButton(
                        parent=self.frame,
                        text="",
                        scale=0.03,
                        pos=(start + x * gstep, 0, 0.35 - y * gstep),
                        command=lambda xx=x, yy=y: self.paint(xx, yy),
                    )
                    row.append(btn)
                self._grid_buttons.append(row)
        else:  # pragma: no cover - tests
            self._grid_buttons = [[None for _ in range(16)] for _ in range(16)]

    # ------------------------------------------------------------------
    def open(self, tile_x: int, tile_y: int) -> None:
        """Open the editor for the given tile."""
        if hasattr(self.base, "tile_click_event"):
            try:
                self._orig_click_handler = self.base.tile_click_event
                self.base.ignore("mouse1")
            except Exception:
                self._orig_click_handler = None
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
        if self._orig_click_handler is not None:
            try:
                self.base.accept("mouse1", self._orig_click_handler)
            except Exception:
                pass
            self._orig_click_handler = None
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
