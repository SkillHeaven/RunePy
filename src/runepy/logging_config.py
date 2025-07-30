import logging
from pathlib import Path

_ROOT_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = _ROOT_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Configure loggers
FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"


class _ExactLevelFilter(logging.Filter):
    """Filter that only passes records matching ``level`` exactly."""

    def __init__(self, level: int) -> None:
        super().__init__()
        self.level = level

    def filter(self, record: logging.LogRecord) -> bool:  # pragma: no cover - trivial
        return record.levelno == self.level


info_handler = logging.FileHandler(str(LOG_DIR / "runepy.log"))
info_handler.setLevel(logging.INFO)

warning_handler = logging.FileHandler(str(LOG_DIR / "warnings.log"))
warning_handler.setLevel(logging.WARNING)
warning_handler.addFilter(_ExactLevelFilter(logging.WARNING))

error_handler = logging.FileHandler(str(LOG_DIR / "errors.log"))
error_handler.setLevel(logging.ERROR)

handlers = [info_handler, warning_handler, error_handler]

logging.basicConfig(level=logging.INFO, format=FORMAT, handlers=handlers)
logging.captureWarnings(True)
