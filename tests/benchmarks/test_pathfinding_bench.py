"""Benchmarking for pathfinding A* implementation.

This test uses ``pytest-benchmark`` to measure the performance of
``runepy.pathfinding.a_star`` on uniformly walkable grids of varying
sizes.

Results on this machine (after numpy vectorisation and neighbour-pruning
optimisation):

- 50×50 grid: ~1.48 ms
- 100×100 grid: ~3.28 ms
- 200×200 grid: ~6.79 ms
"""

import numpy as np

from runepy.pathfinding import a_star


def _run_a_star(size: int) -> None:
    grid = np.ones((size, size), dtype=int)
    start = (0, 0)
    end = (size - 1, size - 1)
    a_star(grid, start, end)


def test_a_star_50(benchmark):
    benchmark(_run_a_star, 50)


def test_a_star_100(benchmark):
    benchmark(_run_a_star, 100)


def test_a_star_200(benchmark):
    benchmark(_run_a_star, 200)
