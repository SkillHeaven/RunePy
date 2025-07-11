from __future__ import annotations

"""Standalone UI editing application."""

try:
    from direct.showbase.ShowBase import ShowBase
except Exception:  # pragma: no cover - Panda3D may be missing
    ShowBase = object  # type: ignore

from pathlib import Path
from runepy.ui.editor import UIEditorController, dump_layout
from runepy.debug import get_debug


class UIEditorApp(ShowBase):
    """Minimal window for editing UI layouts."""

    def __init__(self) -> None:
        super().__init__()
        dbg = get_debug()
        dbg.attach(self)
        self.editor: UIEditorController | None = None
        if dbg.window is not None:
            dbg.window.show()
            self.editor = UIEditorController(dbg.window)
            self.editor.enable()
        self.accept("control-s", self.save_layout)
        self.setBackgroundColor(0.1, 0.1, 0.1)

    def save_layout(self) -> None:
        """Save the current UI layout."""
        if self.editor is None:
            return
        path = Path("debug_layout.json")
        try:
            dump_layout(get_debug().window, path)  # type: ignore[arg-type]
            print(f"Layout saved to {path}")
        except Exception:
            pass


def main() -> None:
    app = UIEditorApp()
    app.run()


if __name__ == "__main__":
    main()
