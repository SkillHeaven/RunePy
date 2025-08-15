from runepy import pathfinding


def test_a_star_open_grid():
    grid = [
        [1, 1],
        [1, 1],
    ]
    path = pathfinding.a_star(grid, (0, 0), (1, 1))
    assert path == [(0, 0), (1, 1)]


def test_a_star_blocked_goal():
    grid = [
        [1, 1],
        [1, 0],
    ]
    path = pathfinding.a_star(grid, (0, 0), (1, 1))
    assert path is None


def test_a_star_four_directional():
    grid = [
        [1, 1],
        [1, 1],
    ]
    offsets = [(0, -1), (1, 0), (0, 1), (-1, 0)]
    path = pathfinding.a_star(grid, (0, 0), (1, 1), neighbor_offsets=offsets)
    assert path == [(0, 0), (1, 0), (1, 1)] or path == [(0, 0), (0, 1), (1, 1)]


def test_a_star_weighted_tiles():
    grid = [
        [1, 1, 1],
        [1, 5, 1],
        [1, 1, 1],
    ]
    offsets = [(0, -1), (1, 0), (0, 1), (-1, 0)]
    path = pathfinding.a_star(
        grid, (0, 1), (2, 1), neighbor_offsets=offsets, weighted=True
    )
    assert path[0] == (0, 1) and path[-1] == (2, 1)
    assert (1, 1) not in path


def test_a_star_prefers_cheaper_diagonal():
    grid = [
        [1, 5, 1],
        [5, 1, 5],
        [1, 5, 1],
    ]
    offsets = [
        (0, -1),
        (1, 0),
        (0, 1),
        (-1, 0),
        (1, -1),
        (1, 1),
        (-1, 1),
        (-1, -1),
    ]
    path = pathfinding.a_star(
        grid, (0, 0), (2, 2), neighbor_offsets=offsets, weighted=True
    )
    assert path == [(0, 0), (1, 1), (2, 2)]
    assert (1, 0) not in path and (0, 1) not in path
