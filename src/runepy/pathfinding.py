# pathfinding.py

import heapq
from dataclasses import dataclass
from typing import Iterable, Tuple, Union

import numpy as np


@dataclass(order=True)
class Node:  # pragma: no cover - retained for API compatibility
    position: tuple
    parent: "Node" = None
    g: float = 0
    h: float = 0
    f: float = 0


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
