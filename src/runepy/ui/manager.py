"""Simple UI manager for loading and toggling interface layouts."""

from __future__ import annotations

import importlib
import json
from pathlib import Path
from typing import Any, Dict

from .builder import StubWidget, build_ui

try:
    from direct.gui.DirectGui import DirectFrame
except Exception:  # pragma: no cover - Panda3D may be missing
    DirectFrame = StubWidget  # type: ignore

class UIManager:
    """Manage GUI layouts and their root frames."""

    def __init__(self) -> None:
        self.frames: Dict[str, Any] = {}
        self.widgets: Dict[str, Dict[str, Any]] = {}
        self.meta: Dict[str, Dict[str, Any]] = {}

    # ------------------------------------------------------------------
    def load_ui(self, name: str, layout: str | Dict[str, Any]) -> Any:
        """Load a UI layout from a module, JSON file or dict."""

        if isinstance(layout, str):
            path = Path(layout)
            if path.suffix.lower() == ".json" and path.exists():
                data = json.loads(path.read_text())
            else:
                module = importlib.import_module(layout)
                if not hasattr(module, "LAYOUT"):
                    raise ValueError(f"No LAYOUT in {layout}")
                data = getattr(module, "LAYOUT")
        else:
            data = layout

        spec = dict(data)
        meta = {"tags": spec.pop("tags", [])}
        root = DirectFrame() if DirectFrame is not StubWidget else StubWidget()
        self.widgets[name] = build_ui(root, spec, self)
        self.frames[name] = root
        self.meta[name] = meta
        return root

    # ------------------------------------------------------------------
    def show_ui(self, name: str) -> None:
        """Display the UI if it was loaded."""
        frame = self.frames.get(name)
        if frame is not None and hasattr(frame, "show"):
            frame.show()

    def hide_ui(self, name: str) -> None:
        """Hide the UI if it is currently visible."""
        frame = self.frames.get(name)
        if frame is not None and hasattr(frame, "hide"):
            frame.hide()

    def destroy_ui(self, name: str) -> None:
        """Remove and destroy a loaded UI."""
        frame = self.frames.pop(name, None)
        self.widgets.pop(name, None)
        self.meta.pop(name, None)
        if frame is not None and hasattr(frame, "destroy"):
            frame.destroy()


__all__ = ["UIManager"]
