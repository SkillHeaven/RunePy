# pathfinding.py

import heapq
from dataclasses import dataclass


@dataclass(order=True)
class Node:
    position: tuple
    parent: "Node" = None
    g: float = 0  # Cost from start to current node
    h: float = 0  # Estimated cost from current node to goal
    f: float = 0  # Total cost (g + h)


def a_star(grid, start, end, neighbor_offsets=None, weighted=False):
    """Perform A* pathfinding on a grid using 0 based indices.

    ``grid`` is expected to be a list-of-lists where ``1`` indicates a
    walkable tile. ``start`` and ``end`` should already be translated into
    grid coordinates starting at ``(0, 0)``. Negative coordinates are not
    considered valid and will be ignored.

    ``neighbor_offsets`` allows customizing movement directions. It should
    be a list of ``(dx, dy)`` tuples. If omitted, movement is allowed in all
    8 directions. When ``weighted`` is ``True`` the values in ``grid`` are
    treated as movement costs instead of booleans.
    """

    # Create start and end node
    start_node = Node(start)
    end_node = Node(end)

    # Initialize the start node's heuristic
    start_node.h = abs(start_node.position[0] - end_node.position[0]) + abs(
        start_node.position[1] - end_node.position[1])
    start_node.f = start_node.h

    height = len(grid)
    width = len(grid[0]) if height > 0 else 0

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

    open_heap = []
    open_dict = {}
    closed_set = set()

    heapq.heappush(open_heap, (start_node.f, start_node))
    open_dict[start_node.position] = start_node

    while open_heap:
        # Get the current node with the lowest f value
        _, current_node = heapq.heappop(open_heap)
        if current_node.position in closed_set:
            continue
        # This node may have been superseded by a better path
        if open_dict.get(current_node.position) is not current_node:
            continue
        del open_dict[current_node.position]
        closed_set.add(current_node.position)

        # Check if we've reached our destination
        if current_node.position == end_node.position:
            path = []
            while current_node:
                path.append(current_node.position)
                current_node = current_node.parent
            return path[::-1]  # Return reversed path

        # Get the neighbors
        neighbors = []
        for offset in neighbor_offsets:
            node_position = (
                current_node.position[0] + offset[0],
                current_node.position[1] + offset[1],
            )

            # Skip positions outside the grid
            if not (0 <= node_position[0] < width and 0 <= node_position[1] < height):
                continue

            # Check if the position is walkable
            tile_value = grid[node_position[1]][node_position[0]]
            if tile_value == 0:
                continue

            neighbors.append((Node(node_position, current_node), tile_value))

        # Loop through the neighbors
        for neighbor, tile_value in neighbors:
            # Skip if the neighbor was already evaluated
            if neighbor.position in closed_set:
                continue

            # Create the f, g, and h values
            step_cost = tile_value if weighted else 1
            neighbor.g = current_node.g + step_cost
            neighbor.h = abs(neighbor.position[0] - end_node.position[0]) + abs(
                neighbor.position[1] - end_node.position[1])
            neighbor.f = neighbor.g + neighbor.h

            # Only add the neighbor if it improves a known path
            if add_to_open(open_dict, neighbor):
                heapq.heappush(open_heap, (neighbor.f, neighbor))


def add_to_open(open_dict, neighbor):
    existing = open_dict.get(neighbor.position)
    if existing is not None and neighbor.g >= existing.g:
        return False
    open_dict[neighbor.position] = neighbor
    return True

