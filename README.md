# RunePyv3.1

RunePyv3.1 is a small demonstration project built with [Panda3D](https://www.panda3d.org/). The code creates a grid of tiles and lets a simple character move across the map using A* pathfinding. It provides a basic camera and control system to experiment with Panda3D's API.

## Features

- Tile-based world generated at runtime
- Character model that moves to the clicked tile
- Top‑down camera with zoom controls
- Debug overlay displaying tile information
- Simple collision and ray casting
- Camera zoom limits keep the view between a minimum and maximum height
- Built-in map editor with hotkeys for saving and loading maps

## Repository Layout

| File | Description |
|------|-------------|
| `client.py` | Entry point that opens the window. |
| `world.py` | Map generation logic. |
| `map_editor.py` | Utilities for editing tiles. |
| `Character.py` | Represents the player model and movement logic. |
| `Camera.py` | Manages the camera position and orientation. |
| `Controls.py` | Handles mouse wheel zooming and other input bindings. |
| `collision.py` | Utilities for ray casting with Panda3D's collision system. |
| `pathfinding.py` | Implementation of a basic A* search. |
| `DebugInfo.py` | Draws onscreen debug text such as mouse and tile coordinates. |
| `utils.py` | Shared helpers like `get_mouse_tile_coords`. |

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
python client.py
```

To launch the map editor instead of the game, run:

```bash
python client.py --mode editor
```

A window will open containing a grid of tiles. Clicking on a tile moves the smiley‑face character to that location using pathfinding. Use the mouse wheel to zoom the camera in or out.

Zooming is always handled by the mouse wheel and cannot be changed. In the editor the camera pans up/down with ``W`` and ``S`` while the ``A`` and ``D`` keys for left/right movement remain rebindable.

Press ``Esc`` in either mode to open an options menu where you can rebind the available controls, including the editor's side movement and save/load shortcuts. When this menu is visible, gameplay clicks are ignored so you can't interact with the world through the menu.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.


## Utilities

`utils.py` contains small helper functions used throughout the project. In particular
`get_mouse_tile_coords` and `get_tile_from_mouse` simplify working with the map
editor by translating the mouse position into tile coordinates.
