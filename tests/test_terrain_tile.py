from runepy.terrain import TerrainTile, FLAG_BLOCKED


def test_terrain_tile_flags_and_values():
    tile = TerrainTile(
        corner_heights=(1.0, 2.0, 3.0, 4.0),
        underlay_id=5,
        overlay_id=6,
        overlay_shape=2,
        overlay_rotation=1,
        flags=FLAG_BLOCKED,
    )
    assert tile.corner_heights == (1.0, 2.0, 3.0, 4.0)
    assert tile.underlay_id == 5
    assert tile.overlay_id == 6
    assert tile.overlay_shape == 2
    assert tile.overlay_rotation == 1
    assert tile.flags & FLAG_BLOCKED
    assert not tile.walkable
