import sys

from runepy.verbose import disable, enable


def test_verbose_enable_disable():
    enable()
    try:
        assert sys.gettrace() is not None
    finally:
        disable()
    assert sys.gettrace() is None
