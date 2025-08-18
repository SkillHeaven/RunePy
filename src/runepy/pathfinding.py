# pathfinding.py

import heapq
import logging
import math
from typing import Iterable, Tuple, Union

import numpy as np
from direct.interval.IntervalGlobal import Func, Sequence
from panda3d.core import Vec3

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
    ``(x, y)`` ordering starting at ``(0, 0)``. If no path exists, ``None`` is
    returned.
    """

    def heuristic(a: Tuple[int, int], b: Tuple[int, int]) -> int:
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return max(dx, dy)

    # Use numpy for fast indexing regardless of the initial grid type.
    grid = np.asarray(grid)
    height, width = grid.shape[:2]

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

    offsets_arr = np.asarray(list(neighbor_offsets), dtype=int)

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

        cx, cy = current
        nx = cx + offsets_arr[:, 0]
        ny = cy + offsets_arr[:, 1]
        valid = (0 <= nx) & (nx < width) & (0 <= ny) & (ny < height)
        nx, ny = nx[valid], ny[valid]
        tile_vals = grid[ny, nx]
        if weighted:
            step_costs = tile_vals
        else:
            step_costs = np.ones_like(tile_vals)
        walkable = tile_vals != 0
        nx, ny, step_costs = nx[walkable], ny[walkable], step_costs[walkable]

        for nx_i, ny_i, step_cost in zip(nx, ny, step_costs):
            dx = int(nx_i - cx)
            dy = int(ny_i - cy)
            if dx and dy:
                # Prune diagonals that cut corners.
                if grid[cy, nx_i] == 0 or grid[ny_i, cx] == 0:
                    continue

            neighbor = (int(nx_i), int(ny_i))
            if neighbor in closed_set:
                continue
            g_score = g + int(step_cost)
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
