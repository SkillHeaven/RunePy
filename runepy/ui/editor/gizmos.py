"""UI editor gizmos."""
from __future__ import annotations

try:
    from direct.gui.DirectGui import DirectFrame
except Exception:  # pragma: no cover - Panda3D may be missing
    DirectFrame = object  # type: ignore

from typing import Any


class SelectionGizmo(DirectFrame):
    """Visual rectangle indicating selected widget."""

    def __init__(self, target: Any) -> None:
        super().__init__(frameColor=(1, 1, 0, 0.5))
        self.target = target
        if hasattr(self, "setBin"):
            try:
                self.setBin("fixed", 100)
            except Exception:
                pass
        self.update()

    def update(self) -> None:
        if not hasattr(self.target, "getPos"):
            return
        try:
            self.reparentTo(self.target.getParent())
            self.setPos(self.target.getPos())
            if hasattr(self.target, "__getitem__"):
                fs = self.target["frameSize"]
                self["frameSize"] = fs
        except Exception:
            pass

__all__ = ["SelectionGizmo"]
