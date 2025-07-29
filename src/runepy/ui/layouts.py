"""Static UI layouts used by various components."""

from __future__ import annotations

OPTIONS_MENU_LAYOUT = {
    "type": "frame",
    "frameColor": (0, 0, 0, 0.7),
    "frameSize": (-0.7, 0.7, -0.6, 0.6),
    "children": [
        {
            "type": "button",
            "name": "save_btn",
            "text": "Save",
            "command": "apply",
            "pos": (-0.2, 0, -0.5),
            "scale": 0.05,
        },
        {
            "type": "button",
            "name": "close_btn",
            "text": "Close",
            "command": "close",
            "pos": (0.2, 0, -0.5),
            "scale": 0.05,
        },
    ],
}

EDITOR_TOOLBAR_LAYOUT = {
    "type": "frame",
    "frameColor": (0, 0, 0, 0.7),
    "frameSize": (-1.3, 1.3, -0.05, 0.05),
    "pos": (0, 0, 0.95),
    "children": [
        {
            "type": "option_menu",
            "name": "mode_menu",
            "items": ["Tile", "Interactable"],
            "scale": 0.05,
            "initialitem": 0,
            "command": "_set_mode",
            "pos": (-1.2, 0, 0),
        },
        {
            "type": "button",
            "name": "save_btn",
            "text": "Save",
            "command": "_save_map",
            "scale": 0.05,
            "pos": (0.2, 0, 0),
        },
        {
            "type": "button",
            "name": "texture_btn",
            "text": "Texture",
            "command": "_open_texture_editor",
            "scale": 0.05,
            "pos": (0.5, 0, 0),
        },
        {
            "type": "button",
            "name": "load_btn",
            "text": "Load",
            "command": "_load_map",
            "scale": 0.05,
            "pos": (0.8, 0, 0),
        },
    ],
}

# Build the texture editor layout with palette and grid buttons
_palette_values = [0, 64, 128, 192, 255]
_palette_step = 0.24
_palette_children = [
    {
        "type": "button",
        "name": f"palette_{i}",
        "text": "",
        "frameColor": (val / 255.0, val / 255.0, val / 255.0, 1),
        "scale": 0.05,
        "pos": (-0.55 + i * _palette_step, 0, 0.45),
    }
    for i, val in enumerate(_palette_values)
]

_grid_step = 0.07
_grid_start = -0.5
_grid_children = [
    {
        "type": "button",
        "name": f"cell_{x}_{y}",
        "text": "",
        "scale": 0.03,
        "pos": (_grid_start + x * _grid_step, 0, 0.35 - y * _grid_step),
    }
    for y in range(16)
    for x in range(16)
]

TEXTURE_EDITOR_LAYOUT = {
    "type": "frame",
    "frameColor": (0, 0, 0, 1),
    "frameSize": (-0.6, 0.6, -0.6, 0.6),
    "pos": (0, 0, 0.2),
    "children": _palette_children + _grid_children
    + [
        {
            "type": "button",
            "name": "close_btn",
            "text": "Close",
            "command": "close",
            "scale": 0.05,
            "pos": (0, 0, -0.55),
        }
    ],
}

LOADING_SCREEN_LAYOUT = {
    "type": "frame",
    "frameColor": (0, 0, 0, 1),
    "frameSize": (-1, 1, -1, 1),
    "children": [
        {
            "type": "frame",
            "name": "container",
            "frameColor": (0.4, 0, 0, 1),
            "frameSize": (-0.7, 0.7, -0.15, 0.15),
            "children": [
                {
                    "type": "label",
                    "name": "label",
                    "text": "Loading...",
                    "pos": (0, 0, 0.05),
                    "scale": 0.07,
                    "frameColor": (0, 0, 0, 0),
                },
                {
                    "type": "wait_bar",
                    "name": "bar",
                    "pos": (0, 0, -0.05),
                    "frameSize": (-0.6, 0.6, -0.05, 0.05),
                    "frameColor": (0.2, 0, 0, 1),
                    "barColor": (1, 0, 0, 1),
                    "range": 100,
                    "value": 0,
                },
            ],
        }
    ],
}

__all__ = [
    "OPTIONS_MENU_LAYOUT",
    "EDITOR_TOOLBAR_LAYOUT",
    "TEXTURE_EDITOR_LAYOUT",
    "LOADING_SCREEN_LAYOUT",
]
