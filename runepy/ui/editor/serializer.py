"""Serialize UI layouts to JSON."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


def _serialize(node: Any) -> Dict[str, Any]:
    data: Dict[str, Any] = {}
    name = getattr(node, "getName", lambda: None)()
    if name:
        data["name"] = name
    if hasattr(node, "getPos"):
        pos = node.getPos()
        data["pos"] = [float(pos[0]), float(pos[1]), float(pos[2])]
    if hasattr(node, "__getitem__"):
        try:
            fs = node["frameSize"]
            data["frameSize"] = [float(v) for v in fs]
        except Exception:
            pass
    children: List[Dict[str, Any]] = []
    for child in getattr(node, "getChildren", lambda: [])():
        children.append(_serialize(child))
    if children:
        data["children"] = children
    return data


def dump_layout(root_np: Any, path: str | Path) -> None:
    """Write the layout of ``root_np`` to ``path`` as JSON."""
    data = _serialize(root_np)
    Path(path).write_text(json.dumps(data, indent=2))

__all__ = ["dump_layout"]
