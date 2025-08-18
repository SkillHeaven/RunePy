import runepy.debug as dbg


def test_debug_stub():
    d = dbg.get_debug()
    assert hasattr(d, 'dump_console')
