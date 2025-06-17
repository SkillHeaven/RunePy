# pathfinding.py

from queue import PriorityQueue


class Node:
    def __init__(self, position, parent=None):
        self.position = position
        self.parent = parent
        self.g = 0  # Cost from start to current node
        self.h = 0  # Estimated cost from current node to goal
        self.f = 0  # Total cost (g + h)

    def __eq__(self, other):
        return self.position == other.position

    def __lt__(self, other):
        return self.f < other.f


def a_star(grid, start, end):
    """Perform A* Pathfinding."""

    # Create start and end node
    start_node = Node(start)
    end_node = Node(end)

    open_list = []
    closed_list = []

    open_list.append(start_node)

    while open_list:
        # Get the current node
        current_node = open_list.pop(0)

        # Add the current node to the closed list
        closed_list.append(current_node)

        # Check if we've reached our destination
        if current_node == end_node:
            path = []
            while current_node:
                path.append(current_node.position)
                current_node = current_node.parent
            return path[::-1]  # Return reversed path

        # Get the neighbors
        neighbors = []
        for new_position in [(0, -1), (1, 0), (0, 1), (-1, 0), (-1, -1), (1, 1), (-1, 1), (1, -1)]:
            node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])

            # Check if the position is walkable
            if grid[node_position[1]][node_position[0]] == 0:
                continue

            neighbors.append(Node(node_position, current_node))

        # Loop through the neighbors
        for neighbor in neighbors:
            # Neighbor is on the closed list
            if neighbor in closed_list:
                continue

            # Create the f, g, and h values
            neighbor.g = current_node.g + 1
            neighbor.h = abs(neighbor.position[0] - end_node.position[0]) + abs(
                neighbor.position[1] - end_node.position[1])
            neighbor.f = neighbor.g + neighbor.h

            # Only add the neighbor if it doesn't exist in the open list with
            # a lower cost
            if add_to_open(open_list, neighbor):
                open_list.append(neighbor)


def add_to_open(open_list, neighbor):
    for node in open_list:
        if neighbor == node and neighbor.g > node.g:
            return False
    return True

