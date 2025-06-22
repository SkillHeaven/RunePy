"""Debug utilities for RunePy.

This module exposes a :class:`DebugManager` singleton via :func:`get_debug`.
Importing the package will not raise ImportError even if Panda3D's ``direct``
module is unavailable.
"""

from __future__ import annotations

from typing import Optional

try:
    from .gui import DebugWindow  # type: ignore
except Exception:  # pragma: no cover - GUI components may not be present
    DebugWindow = None  # type: ignore


class DebugManager:
    """Simple container for debug helpers."""

    def __init__(self) -> None:
        self.window: Optional[DebugWindow] = None
        if DebugWindow is not None:
            try:
                self.window = DebugWindow(self)
            except Exception:
                # Failed to initialize debug window (likely no Panda3D)
                self.window = None

    def toggle(self) -> None:
        """Toggle visibility of the debug window if available."""
        if self.window is None:
            return
        if self.window.isHidden():
            self.window.show()
        else:
            self.window.hide()


_debug_instance: Optional[DebugManager] = None


def get_debug() -> DebugManager:
    """Return the shared :class:`DebugManager` instance."""
    global _debug_instance
    if _debug_instance is None:
        _debug_instance = DebugManager()
    return _debug_instance


__all__ = ["DebugManager", "get_debug"]
