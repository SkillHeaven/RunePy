"""Utility to build UI widgets from a layout dictionary."""
from __future__ import annotations

from typing import Any, Dict

try:
    from direct.gui.DirectGui import (
        DirectFrame,
        DirectButton,
        DirectSlider,
        DirectLabel,
        DirectEntry,
        DirectOptionMenu,
        DirectWaitBar,
    )
except Exception:  # pragma: no cover - Panda3D may be missing
    DirectFrame = None  # type: ignore
    DirectButton = None  # type: ignore
    DirectSlider = None  # type: ignore
    DirectLabel = None  # type: ignore
    DirectEntry = None  # type: ignore
    DirectOptionMenu = None  # type: ignore
    DirectWaitBar = None  # type: ignore


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

    def __setitem__(
        self, key: str, value: Any
    ) -> None:  # pragma: no cover - stub
        self._props[key] = value


_WIDGETS = {
    "frame": DirectFrame or StubWidget,
    "label": DirectLabel or StubWidget,
    "button": DirectButton or StubWidget,
    "slider": DirectSlider or StubWidget,
    "entry": DirectEntry or StubWidget,
    "option_menu": DirectOptionMenu or StubWidget,
    "wait_bar": DirectWaitBar or StubWidget,
}


def _make_widget(kind: str, parent: Any, **kwargs: Any) -> Any:
    cls = _WIDGETS[kind]
    if cls is None:
        cls = StubWidget
    w = cls(parent=parent, **kwargs)
    if hasattr(w, "setPythonTag"):
        w.setPythonTag("debug_gui", True)
    return w


def _build_slider(parent: Any, spec: Dict[str, Any], mgr: Any) -> Any:
    getter = getattr(mgr, spec['getter'])
    setter = getattr(mgr, spec['setter'])

    # DirectSlider passes the new value as its first positional arg.
    # Preserve that parameter in the lambda.
    props = dict(spec.get('props', {}))
    rng = props.pop('range', spec.get('range', (0, 1)))
    val = props.pop('value', getter())

    slider = DirectSlider(
        parent=parent,
        range=rng,
        value=val,
        **props,
    )
    slider["command"] = lambda _s=slider, _setter=setter: _setter(
        float(_s["value"])
    )
    return slider


def build_ui(
    parent: Any,
    layout: Dict[str, Any],
    manager: Any | None = None,
) -> Dict[str, Any]:
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
                "tags",
            }
        }
        if "pos" in params:
            params["pos"] = tuple(params["pos"])
        if "frameSize" in params:
            params["frameSize"] = tuple(params["frameSize"])

        if kind == "button":
            cmd_name = node.get("command")
            cmd = (
                getattr(manager, cmd_name)
                if manager and cmd_name and hasattr(manager, cmd_name)
                else None
            )
            if cmd is not None:
                params["command"] = cmd
            widget = _make_widget("button", parent_node, **params)
        elif kind == "option_menu":
            cmd_name = node.get("command")
            cmd = (getattr(manager, cmd_name) if manager and cmd_name and hasattr(manager, cmd_name) else None)
            if cmd is not None:
                params["command"] = cmd
            widget = _make_widget("option_menu", parent_node, **params)
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
                    value = getattr(manager, getter_name)()
                except Exception:
                    value = None
            else:
                value = None
            if setter_name and manager and hasattr(manager, setter_name):
                props = params.copy()
                if value is not None:
                    props.setdefault("value", value)
                spec = {
                    "getter": getter_name,
                    "setter": setter_name,
                    "range": props.get("range", (0, 1)),
                    "props": props,
                }
                widget = _build_slider(parent_node, spec, manager)
            else:
                if value is not None:
                    params.setdefault("value", value)
                widget = _make_widget("slider", parent_node, **params)
        elif kind == "wait_bar":
            widget = _make_widget("wait_bar", parent_node, **params)
        elif kind == "entry":
            widget = _make_widget("entry", parent_node, **params)
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
