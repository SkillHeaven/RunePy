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
