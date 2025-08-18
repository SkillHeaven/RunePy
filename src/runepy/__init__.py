"""RunePy package."""

from . import (
    logging_config,  # noqa: F401
    pathfinding,
    verbose,
)
from .array_map import RegionArrays
from .input_binder import InputBinder
from .map_manager import MapManager
from .pathfinding import Pathfinder
from .terrain import FLAG_BLOCKED, TerrainTile
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
    "Pathfinder",
    "InputBinder",
    "verbose",
]
