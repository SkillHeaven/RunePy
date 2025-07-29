from __future__ import annotations

"""Shared UI helpers."""

from typing import Any, Dict

from .builder import build_ui, StubWidget

try:
    from direct.gui.DirectGui import DirectFrame
except Exception:  # pragma: no cover - Panda3D may be missing
    DirectFrame = StubWidget  # type: ignore


def create_ui(layout: Dict[str, Any], manager: Any | None = None, parent: Any | None = None):
    """Return ``(frame, widgets)`` built from ``layout``."""
    root = DirectFrame(parent=parent) if DirectFrame is not StubWidget else StubWidget()
    widgets = build_ui(root, layout, manager)
    return root, widgets

__all__ = ["create_ui"]
