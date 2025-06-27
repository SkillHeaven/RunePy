# RunePy

RunePy is a small demonstration project built with [Panda3D](https://www.panda3d.org/). It generates a tiled world where a simple character moves using A* pathfinding. Regions stream in dynamically as you explore and the project provides a basic camera and control system to experiment with Panda3D's API.

## Features

- Tile-based world generated at runtime
- Character model that moves to the clicked tile
- Top‑down camera with zoom controls
- Debug overlay displaying tile information
- Simple collision and ray casting
- Camera zoom limits keep the view between a minimum and maximum height
- Built-in map editor with hotkeys for saving and loading maps
- Tiles support custom metadata loaded from map files
- Individual tiles darken slightly when hovered to show the current mouse position
- Loading screen displays progress messages during startup
- Map regions stream in on demand as the player moves
- Placeholder debug window toggled with ``F1``
- Centralized UI manager for loading and toggling interfaces

## Repository Layout

| File | Description |
|------|-------------|
| `runepy/client.py` | Entry point that opens the window. |
| `runepy/world.py` | Map generation logic. |
| `runepy/map_editor.py` | Utilities for editing tiles. |
| `runepy/character.py` | Represents the player model and movement logic. |
| `runepy/camera.py` | Manages the camera position and orientation. |
| `runepy/controls.py` | Handles mouse wheel zooming and other input bindings. |
| `runepy/collision.py` | Utilities for ray casting with Panda3D's collision system. |
| `runepy/pathfinding.py` | Implementation of a basic A* search with optional weighted costs and movement patterns. |
| `runepy/debuginfo.py` | Draws onscreen debug text such as mouse and tile coordinates. |
| `runepy/utils.py` | Shared helpers like `get_mouse_tile_coords`. |
| `runepy/debug/manager.py` | Toggleable debug window and related tools. |
| `runepy/ui/builder.py` | Constructs GUI widgets from layout dictionaries. |
| `runepy/ui/manager.py` | Simple manager for loading and showing UIs. |
| `runepy/ui/editor` | Package providing the simple UI editor. |
| `runepy/ui_editor.py` | Standalone UI editing window. |

## Requirements

- Python 3
- [Panda3D](https://www.panda3d.org/) 1.10 or newer

Install Panda3D using `pip` if it is not already available:

```bash
pip install panda3d
```

## Running the example

After installing the requirements, launch the program using one of the following commands:

**Windows PowerShell**
```powershell
./run.ps1
```

**Direct Python**
```bash
python -m runepy.client
```

To launch the map editor instead of the game, run:

```bash
python -m runepy.client --mode editor
```

To open the standalone UI editor, run:

```bash
python -m runepy.ui_editor
```

A window will open containing a grid of tiles. The world loads 64×64 regions dynamically as you explore, letting the map expand as needed. Clicking on a tile moves the smiley‑face character to that location using pathfinding. Use the mouse wheel to zoom the camera in or out.

Zooming is always handled by the mouse wheel and cannot be changed. In the editor the camera pans up/down with ``W`` and ``S`` while the ``A`` and ``D`` keys for left/right movement remain rebindable.

Press ``Esc`` in either mode to open an options menu where you can rebind the available controls, including the editor's side movement and save/load shortcuts. When this menu is visible, gameplay clicks are ignored so you can't interact with the world through the menu.

Press ``F1`` at any time to toggle a minimal debug window. The old stats and
sliders have been removed while the feature is being reworked.

## Configuration

Default key bindings are defined in ``config.json`` at the repository root. Edit this file to customize the controls that are initially loaded by both the game and the editor.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Numeric map layers

`array_map.py` contains a `RegionArrays` helper for storing map data in
efficient `numpy` arrays. Each layer (height, terrain, overlay and collision)
is saved to a single `.npz` archive:

```python
from runepy.array_map import RegionArrays

region = RegionArrays.empty((64, 64))
region.save("region_01.npz")
loaded = RegionArrays.load("region_01.npz")
```

## Map Manager and region loading

The world is divided into 64×64 tile regions that are loaded on demand. The
``MapManager`` class tracks the player position and ensures all regions within a
view radius remain loaded. Region coordinates are computed with ``Rx = x //
64`` and ``Ry = y // 64`` and a unique ID may be derived from ``(Rx << 8) | Ry``.
When the player crosses a region boundary, adjacent regions are loaded and old
ones are unloaded automatically.

```python
from runepy import MapManager

manager = MapManager(view_distance=1)
manager.update(10, 20)  # loads the region containing (10,20) and neighbors
manager.update(70, 20)  # moves into the next region triggering load/unload
```



## Utilities

`utils.py` contains small helper functions used throughout the project. In particular
`get_mouse_tile_coords` and `get_tile_from_mouse` translate the mouse position into
tile coordinates using the camera and render nodes. Pass the current camera and
`render` root when calling these helpers.

## Tests

Install the Python dependencies listed in `requirements.txt` and run the
test suite with `pytest -q` from the repository root:

```bash
pip install -r requirements.txt
pytest -q
```

All tests should pass. The suite includes checks for pathfinding, region
streaming and the debug utilities.
