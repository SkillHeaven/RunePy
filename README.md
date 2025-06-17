# RunePyv3.1

RunePyv3.1 is a small demonstration project built with [Panda3D](https://www.panda3d.org/). The code creates a grid of tiles and lets a simple character move across the map using A* pathfinding. It provides a basic camera and control system to experiment with Panda3D's API.

## Features

- Tile-based world generated at runtime
- Character model that moves to the clicked tile
- Top‑down camera with zoom controls
- Debug overlay displaying tile information
- Simple collision and ray casting

## Repository Layout

| File | Description |
|------|-------------|
| `TileMap.py` | Entry point that builds the world and handles input. |
| `Character.py` | Represents the player model and movement logic. |
| `Camera.py` | Manages the camera position and orientation. |
| `Controls.py` | Handles mouse wheel zooming and other input bindings. |
| `collision.py` | Utilities for ray casting with Panda3D's collision system. |
| `pathfinding.py` | Implementation of a basic A* search. |
| `DebugInfo.py` | Draws onscreen debug text such as mouse and tile coordinates. |

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
python TileMap.py
```

A window will open containing a grid of tiles. Clicking on a tile moves the smiley‑face character to that location using pathfinding. Use the mouse wheel to zoom the camera in or out.

## License

This project is provided as a minimal example without any specific license. Feel free to reuse the code for your own experiments with Panda3D.

