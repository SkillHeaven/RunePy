"""RunePy package."""

from . import pathfinding
from .array_map import RegionArrays
from .map_manager import MapManager
from .terrain import TerrainTile, FLAG_BLOCKED
from .ui.manager import UIManager

try:
    from .base_app import BaseApp
except Exception:
    BaseApp = None  # Panda3D may not be available during tests

__all__ = [
    "pathfinding",
    "BaseApp",
    "RegionArrays",
    "MapManager",
    "TerrainTile",
    "FLAG_BLOCKED",
    "UIManager",
]

