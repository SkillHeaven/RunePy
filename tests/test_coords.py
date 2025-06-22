from constants import REGION_SIZE
from world.coords import world_to_region, local_tile


def round_trip(x, y):
    rx, ry = world_to_region(x, y)
    lx, ly = local_tile(x, y)
    wx = rx * REGION_SIZE + lx
    wy = ry * REGION_SIZE + ly
    return wx, wy


def test_round_trip_zero():
    assert round_trip(0, 0) == (0, 0)


def test_round_trip_boundary():
    assert round_trip(63, 63) == (63, 63)
    assert round_trip(64, 64) == (64, 64)


def test_round_trip_misc():
    samples = [
        (65, 20),
        (-1, -1),
        (-65, -65),
        (128, 130),
    ]
    for x, y in samples:
        assert round_trip(x, y) == (x, y)
