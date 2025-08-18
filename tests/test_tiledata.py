from runepy.world.world import TileData


def test_tiledata_round_trip_custom_props():
    tile = TileData(walkable=False, description="foo", properties={"cost": 5})
    data = tile.to_dict()
    assert data["cost"] == 5
    loaded = TileData.from_dict(data)
    assert loaded.properties["cost"] == 5
    assert not loaded.walkable
    assert loaded.description == "foo"

