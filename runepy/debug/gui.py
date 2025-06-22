"""GUI components for debugging.

This module wraps Panda3D's DirectGUI widgets. It can be imported safely even
when Panda3D is not available.
"""

from __future__ import annotations

try:
    from direct.gui.DirectGui import (
        DirectFrame,
        DirectButton,
        DirectSlider,
        DirectLabel,
    )
    from direct.task import Task
except Exception:  # pragma: no cover - Panda3D may be missing
    DirectFrame = object  # type: ignore
    DirectButton = object  # type: ignore
    DirectSlider = object  # type: ignore
    DirectLabel = object  # type: ignore
    Task = object  # type: ignore


class DebugWindow(DirectFrame):
    def __init__(self, mgr) -> None:
        super().__init__(
            frameColor=(0, 0, 0, 0.7),
            frameSize=(-0.6, 0.6, -0.4, 0.4),
            pos=(0.7, 0, 0.55),
        )
        self.mgr = mgr  # back-reference
        self._build_live_stats()
        self._build_actions()
        self._build_tweaks()
        self.hide()

    def _build_live_stats(self) -> None:
        pass

    def _build_actions(self) -> None:
        pass

    def _build_tweaks(self) -> None:
        pass

__all__ = ["DebugWindow"]
