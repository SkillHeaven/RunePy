"""Utility to build UI widgets from a layout dictionary."""
from __future__ import annotations

from typing import Any, Dict

try:
    from direct.gui.DirectGui import DirectFrame, DirectButton, DirectSlider, DirectLabel
except Exception:  # pragma: no cover - Panda3D may be missing
    DirectFrame = None  # type: ignore
    DirectButton = None  # type: ignore
    DirectSlider = None  # type: ignore
    DirectLabel = None  # type: ignore


class StubWidget:
    """Fallback widget used when Panda3D is unavailable."""

    def __init__(self, **kwargs: Any) -> None:
        self._props: Dict[str, Any] = kwargs

    def hide(self) -> None:  # pragma: no cover - stub
        pass

    def show(self) -> None:  # pragma: no cover - stub
        pass

    def destroy(self) -> None:  # pragma: no cover - stub
        pass

    def setPythonTag(self, *args: Any) -> None:  # pragma: no cover - stub
        pass

    def __getitem__(self, key: str) -> Any:  # pragma: no cover - stub
        return self._props.get(key)

    def __setitem__(self, key: str, value: Any) -> None:  # pragma: no cover - stub
        self._props[key] = value


_WIDGETS = {
    "frame": DirectFrame or StubWidget,
    "label": DirectLabel or StubWidget,
    "button": DirectButton or StubWidget,
    "slider": DirectSlider or StubWidget,
}


def _make_widget(kind: str, parent: Any, **kwargs: Any) -> Any:
    cls = _WIDGETS[kind]
    if cls is None:
        cls = StubWidget
    w = cls(parent=parent, **kwargs)
    if hasattr(w, "setPythonTag"):
        w.setPythonTag("debug_gui", True)
    return w


def build_ui(parent: Any, layout: Dict[str, Any], manager: Any | None = None) -> Dict[str, Any]:
    """Create widgets from ``layout`` and return them in a dict."""

    widgets: Dict[str, Any] = {}

    def _build(node: Dict[str, Any], parent_node: Any) -> None:
        kind = node.get("type")
        name = node.get("name")
        children = node.get("children", [])
        params = {
            k: v
            for k, v in node.items()
            if k
            not in {
                "type",
                "name",
                "children",
                "command",
                "getter",
                "setter",
                "label",
                "label_pos",
                "label_scale",
                "range",
            }
        }

        if kind == "button":
            cmd_name = node.get("command")
            cmd = getattr(manager, cmd_name) if manager and cmd_name and hasattr(manager, cmd_name) else None
            if cmd is not None:
                params["command"] = cmd
            widget = _make_widget("button", parent_node, **params)
        elif kind == "slider":
            label_text = node.get("label") or node.get("text")
            label_pos = node.get("label_pos")
            label_scale = node.get("label_scale")
            if label_text is not None:
                lkw = {"text": label_text}
                if label_pos is not None:
                    lkw["pos"] = tuple(label_pos)
                if label_scale is not None:
                    lkw["scale"] = label_scale
                _make_widget("label", parent_node, **lkw)
            getter_name = node.get("getter")
            setter_name = node.get("setter")
            rng = node.get("range")
            if rng is not None:
                params["range"] = tuple(rng)
            if getter_name and manager and hasattr(manager, getter_name):
                try:
                    params["value"] = getattr(manager, getter_name)()
                except Exception:
                    pass
            if setter_name and manager and hasattr(manager, setter_name):
                def _cb(v: Any, m=manager, n=setter_name):
                    try:
                        getattr(m, n)(float(v))
                    except Exception:
                        pass
                params["command"] = _cb
            widget = _make_widget("slider", parent_node, **params)
        elif kind == "label":
            widget = _make_widget("label", parent_node, **params)
        elif kind == "frame":
            widget = _make_widget("frame", parent_node, **params)
        else:
            return

        if name:
            widgets[name] = widget
        for child in children:
            _build(child, widget)

    _build(layout, parent)
    return widgets

__all__ = ["build_ui", "StubWidget"]

