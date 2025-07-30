# pathfinding.py

import heapq
from typing import Iterable, Tuple, Union

import logging
import math
from panda3d.core import Vec3
from direct.interval.IntervalGlobal import Sequence, Func

import numpy as np

logger = logging.getLogger(__name__)


def a_star(
    grid: Union[list, np.ndarray],
    start: Tuple[int, int],
    end: Tuple[int, int],
    neighbor_offsets: Iterable[Tuple[int, int]] | None = None,
    weighted: bool = False,
):
    """Perform A* pathfinding on ``grid`` and return the path as a list.

    ``grid`` may be a list-of-lists or :class:`numpy.ndarray` with ``1`` values
    indicating walkable tiles. ``start`` and ``end`` are grid coordinates using
    ``(x, y)`` ordering starting at ``(0, 0)``.
    """

    def heuristic(a: Tuple[int, int], b: Tuple[int, int]) -> int:
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if isinstance(grid, np.ndarray):
        height, width = grid.shape[:2]

        def value(x: int, y: int):
            return grid[y, x]
    else:
        height = len(grid)
        width = len(grid[0]) if height > 0 else 0

        def value(x: int, y: int):
            return grid[y][x]

    if neighbor_offsets is None:
        neighbor_offsets = [
            (0, -1),
            (1, 0),
            (0, 1),
            (-1, 0),
            (-1, -1),
            (1, 1),
            (-1, 1),
            (1, -1),
        ]

    open_heap: list[tuple[float, Tuple[int, int]]] = []
    open_dict: dict[Tuple[int, int], tuple[float, Tuple[int, int] | None]] = {}
    closed_set: set[Tuple[int, int]] = set()

    start_h = heuristic(start, end)
    open_dict[start] = (0.0, None)
    heapq.heappush(open_heap, (start_h, start))

    while open_heap:
        current_f, current = heapq.heappop(open_heap)
        data = open_dict.get(current)
        if data is None:
            continue
        g, parent = data
        if current in closed_set:
            continue
        if current == end:
            path = []
            pos = current
            while pos is not None:
                path.append(pos)
                pos = open_dict[pos][1]
            return path[::-1]

        closed_set.add(current)

        for dx, dy in neighbor_offsets:
            nx, ny = current[0] + dx, current[1] + dy
            if not (0 <= nx < width and 0 <= ny < height):
                continue
            tile_val = value(nx, ny)
            if tile_val == 0:
                continue
            step_cost = tile_val if weighted else 1
            g_score = g + step_cost
            neighbor = (nx, ny)
            if neighbor in closed_set:
                continue
            h_score = heuristic(neighbor, end)
            existing = open_dict.get(neighbor)
            if existing is not None and g_score >= existing[0]:
                continue
            open_dict[neighbor] = (g_score, current)
            heapq.heappush(open_heap, (g_score + h_score, neighbor))

    return None

class Pathfinder:
    """Helper to compute paths and move a character along them."""

    def __init__(self, character, world, camera_control, debug=False):
        self.character = character
        self.world = world
        self.camera_control = camera_control
        self.debug = debug

    def log(self, *args, **kwargs):
        if self.debug:
            logger.debug(*args, **kwargs)

    def move_along_path(self, target_x: int, target_y: int) -> None:
        """Find a path to ``(target_x, target_y)`` and move the character."""
        current_pos = self.character.get_position()
        target_pos = Vec3(target_x, target_y, current_pos.getZ())
        if (current_pos - target_pos).length() <= 0.1:
            self.log("Already at destination")
            return

        self.character.cancel_movement()
        current_x, current_y = int(current_pos.getX()), int(current_pos.getY())

        stitched, off_x, off_y = self.world.walkable_window(current_x, current_y)
        start_idx = (current_x - off_x, current_y - off_y)
        end_idx = (target_x - off_x, target_y - off_y)

        path = a_star(stitched, start_idx, end_idx)
        self.log("Calculated Path:", path)
        if not path:
            return
        if path and path[0] == start_idx:
            path = path[1:]
        if not path:
            self.log("Already at destination")
            return

        intervals = []
        prev_x, prev_y = current_pos.getX(), current_pos.getY()
        for step in path:
            world_x = step[0] + off_x
            world_y = step[1] + off_y
            distance = math.sqrt((world_x - prev_x) ** 2 + (world_y - prev_y) ** 2)
            duration = distance / self.character.speed
            move_interval = self.character.move_to(Vec3(world_x, world_y, 0.5), duration)
            intervals.append(move_interval)
            prev_x, prev_y = world_x, world_y

        seq = Sequence(*intervals, Func(self.camera_control.update_camera_focus))
        self.character.start_sequence(seq)

