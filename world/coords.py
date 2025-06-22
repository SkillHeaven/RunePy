from constants import REGION_SIZE


def world_to_region(x: int, y: int) -> tuple[int, int]:
    return x // REGION_SIZE, y // REGION_SIZE


def local_tile(x: int, y: int) -> tuple[int, int]:
    return x % REGION_SIZE, y % REGION_SIZE
