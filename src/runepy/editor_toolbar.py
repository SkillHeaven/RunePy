"""Editor toolbar UI for choosing edit mode and saving/loading."""
from __future__ import annotations

try:
    from direct.gui.DirectGui import DirectFrame, DirectOptionMenu, DirectButton
except Exception:  # pragma: no cover - Panda3D may be missing
    DirectFrame = object  # type: ignore
    DirectOptionMenu = object  # type: ignore
    DirectButton = object  # type: ignore


class EditorToolbar:
    """Top-of-screen toolbar for the map editor."""

    def __init__(self, base, editor) -> None:
        self.base = base
        self.editor = editor
        if DirectFrame is object:
            self.frame = None
            return
        self.frame = DirectFrame(
            frameColor=(0, 0, 0, 0.7),
            frameSize=(-1.3, 1.3, -0.05, 0.05),
            pos=(0, 0, 0.95),
        )
        self.mode_menu = DirectOptionMenu(
            parent=self.frame,
            items=["Tile", "Interactable"],
            scale=0.05,
            initialitem=0,
            command=self._set_mode,
            pos=(-1.2, 0, 0),
        )
        DirectButton(
            parent=self.frame,
            text="Save",
            scale=0.05,
            pos=(0.2, 0, 0),
            command=self.editor.save_map,
        )
        DirectButton(
            parent=self.frame,
            text="Texture",
            scale=0.05,
            pos=(0.5, 0, 0),
            command=self.editor.open_texture_editor,
        )
        DirectButton(
            parent=self.frame,
            text="Load",
            scale=0.05,
            pos=(0.8, 0, 0),
            command=self.editor.load_map,
        )

    # ------------------------------------------------------------------
    def _set_mode(self, choice: str) -> None:
        self.editor.set_mode(choice.lower())

    def destroy(self) -> None:
        if self.frame is not None and hasattr(self.frame, "destroy"):
            self.frame.destroy()
            self.frame = None


__all__ = ["EditorToolbar"]
