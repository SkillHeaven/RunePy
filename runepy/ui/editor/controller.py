"""UI editing controller."""
from __future__ import annotations

try:
    from direct.showbase.ShowBaseGlobal import base
    from direct.task import Task
except Exception:  # pragma: no cover - Panda3D may be missing
    base = None  # type: ignore
    Task = object  # type: ignore

try:
    from direct.gui.DirectGui import DirectFrame
except Exception:  # pragma: no cover - Panda3D may be missing
    DirectFrame = object  # type: ignore

from pathlib import Path
from typing import Any
import os
import sys

try:
    from panda3d.core import WindowProperties
except Exception:  # pragma: no cover - Panda3D may be missing
    WindowProperties = object  # type: ignore

from .serializer import dump_layout
from .gizmos import SelectionGizmo


class UIEditorController:
    """Basic UI layout editor."""

    def __init__(self, root_np: Any) -> None:
        self.root = root_np
        self._drag_widget = None
        self._drag_start = None
        self._widget_start = None
        self._gizmo: SelectionGizmo | None = None

    # ------------------------------------------------------------------
    def enable(self) -> None:
        if base is None:
            return
        base.accept("control-s", self._save)
        base.accept("arrow_up", lambda: self._nudge(0, 0.01))
        base.accept("arrow_down", lambda: self._nudge(0, -0.01))
        base.accept("arrow_left", lambda: self._nudge(-0.01, 0))
        base.accept("arrow_right", lambda: self._nudge(0.01, 0))
        base.accept("mouse1", self._mouse_down)
        base.accept("mouse1-up", self._mouse_up)
        base.taskMgr.add(self._on_mouse_move, "ui-editor-move")
        if WindowProperties is not object and hasattr(base, "win"):
            try:
                props = WindowProperties()
                cursor=""
                if sys.platform.startswith("win"):
                    root=os.environ.get("SystemRoot", r"C:\Windows")
                    candidate=Path(root)/"Cursors"/"cross.cur"
                    if candidate.exists():
                        cursor=str(candidate)
                if cursor:
                    props.setCursorFilename(cursor)
                base.win.requestProperties(props)
            except Exception:
                pass

    def disable(self) -> None:
        if base is None:
            return
        base.ignore("control-s")
        for key in ("arrow_up", "arrow_down", "arrow_left", "arrow_right"):
            base.ignore(key)
        base.ignore("mouse1")
        base.ignore("mouse1-up")
        base.taskMgr.remove("ui-editor-move")
        if self._gizmo is not None:
            try:
                self._gizmo.destroy()
            except Exception:
                pass
            self._gizmo = None
        if WindowProperties is not object and hasattr(base, "win"):
            try:
                props = WindowProperties()
                props.setCursorFilename("")
                base.win.requestProperties(props)
            except Exception:
                pass

    # ------------------------------------------------------------------
    def _on_mouse_move(self, task: "Task"):
        if base is None or not base.mouseWatcherNode.hasMouse():
            return task.cont
        mpos = base.mouseWatcherNode.getMouse()
        if base.mouseWatcherNode.is_button_down("mouse1") and self._drag_widget:
            return self._update_drag(task)
        return task.cont

    def _mouse_down(self) -> None:
        if base is None or not base.mouseWatcherNode.hasMouse():
            return
        mpos = base.mouseWatcherNode.getMouse()

        def _search(node: Any) -> Any | None:
            for child in getattr(node, "getChildren", lambda: [])():
                found = _search(child)
                if found is not None:
                    return found
            if getattr(node, "getPythonTag", lambda _n: None)("debug_gui"):
                if hasattr(node, "__getitem__") and hasattr(node, "getPos"):
                    try:
                        fs = node["frameSize"]
                        pos = node.getPos()
                        left = pos[0] + fs[0]
                        right = pos[0] + fs[1]
                        bottom = pos[2] + fs[2]
                        top = pos[2] + fs[3]
                        if left <= mpos[0] <= right and bottom <= mpos[1] <= top:
                            return node
                    except Exception:
                        pass
            return None

        widget = _search(self.root)
        if widget is not None:
            self._begin_drag(widget, mpos)

    def _mouse_up(self) -> None:
        self._finish_drag()

    def _begin_drag(self, widget: Any, mpos: Any) -> None:
        self._drag_widget = widget
        self._drag_start = mpos
        if hasattr(widget, "getPos"):
            self._widget_start = widget.getPos()
        if self._gizmo is None:
            try:
                self._gizmo = SelectionGizmo(widget)
            except Exception:
                self._gizmo = None
        else:
            self._gizmo.target = widget  # type: ignore[attr-defined]
            self._gizmo.update()  # type: ignore[operator]
        base.taskMgr.add(self._update_drag, "ui-editor-drag")

    def _update_drag(self, task: "Task"):
        if base is None or self._drag_widget is None or self._drag_start is None:
            return task.done
        if not base.mouseWatcherNode.hasMouse():
            return task.cont
        cur = base.mouseWatcherNode.getMouse()
        dx = cur[0] - self._drag_start[0]
        dy = cur[1] - self._drag_start[1]
        if self._widget_start is not None and hasattr(self._drag_widget, "setPos"):
            self._drag_widget.setPos(
                self._widget_start[0] + dx,
                0,
                self._widget_start[2] + dy,
            )
            if self._gizmo is not None:
                self._gizmo.update()
        return task.cont

    def _finish_drag(self) -> None:
        self._drag_widget = None
        self._drag_start = None
        self._widget_start = None
        try:
            base.taskMgr.remove("ui-editor-drag")
        except Exception:
            pass

    # ------------------------------------------------------------------
    def _nudge(self, dx: float, dz: float) -> None:
        if self._gizmo is None:
            return
        widget = self._gizmo.target
        if widget is None or not hasattr(widget, "getPos"):
            return
        pos = widget.getPos()
        widget.setPos(pos[0] + dx, 0, pos[2] + dz)
        self._gizmo.update()

    def _save(self) -> None:
        path = Path(__file__).with_name("debug_layout.json")
        try:
            dump_layout(self.root, path)
            print("layout saved")
        except Exception as exc:  # pragma: no cover - can't save
            print(f"failed to save layout: {exc}")

__all__ = ["UIEditorController"]
