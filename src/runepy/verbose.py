import atexit
import logging
import sys
from types import FrameType

from .logging_config import LOG_DIR

logger = logging.getLogger("runepy.verbose")
FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
_verbose_handler = logging.FileHandler(str(LOG_DIR / "verbose.log"))
_verbose_handler.setLevel(logging.DEBUG)
_verbose_handler.setFormatter(logging.Formatter(FORMAT))
_enabled = False

def _trace(frame: FrameType, event: str, arg):
    if event in {"call", "return", "exception"}:
        code = frame.f_code
        name = f"{code.co_filename}:{code.co_name}:{frame.f_lineno}"
        if event == "call":
            if logger:
                logger.debug("CALL %s", name)
        elif event == "return":
            if logger:
                logger.debug("RETURN %s", name)
        elif event == "exception":
            exc_type, exc_val, _ = arg
            if logger:
                logger.debug(
                    "EXCEPTION %s %s: %s", name, exc_type.__name__, exc_val
                )
    return _trace


def enable() -> None:
    """Enable verbose tracing and log all function calls."""
    global _enabled
    if _enabled:
        return
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.addHandler(_verbose_handler)
    sys.settrace(_trace)
    atexit.register(disable)
    _enabled = True


def disable() -> None:
    """Disable verbose tracing."""
    global _enabled
    if not _enabled:
        return
    sys.settrace(None)
    root = logging.getLogger()
    root.removeHandler(_verbose_handler)
    _enabled = False
