"""Editor toolbar UI for choosing edit mode and saving/loading."""
from __future__ import annotations

try:
    from direct.gui.DirectGui import DirectFrame, DirectOptionMenu, DirectButton
except Exception:  # pragma: no cover - Panda3D may be missing
    DirectFrame = object  # type: ignore
    DirectOptionMenu = object  # type: ignore
    DirectButton = object  # type: ignore
from runepy.ui.common import create_ui
from runepy.ui.layouts import EDITOR_TOOLBAR_LAYOUT


class EditorToolbar:
    """Top-of-screen toolbar for the map editor."""

    def __init__(self, base, editor) -> None:
        self.base = base
        self.editor = editor
        layout = EDITOR_TOOLBAR_LAYOUT
        self.frame, widgets = create_ui(layout, self)
        self.mode_menu = widgets.get("mode_menu")

    # ------------------------------------------------------------------
    def _set_mode(self, choice: str) -> None:
        self.editor.set_mode(choice.lower())
    def _save_map(self) -> None:
        self.editor.save_map()

    def _open_texture_editor(self) -> None:
        self.editor.open_texture_editor()

    def _load_map(self) -> None:
        self.editor.load_map()


    def destroy(self) -> None:
        if self.frame is not None and hasattr(self.frame, "destroy"):
            self.frame.destroy()
            self.frame = None


__all__ = ["EditorToolbar"]
