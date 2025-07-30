import logging
from pathlib import Path
_ROOT_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = _ROOT_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)


# Configure loggers
FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
runepy_handler = logging.FileHandler(str(LOG_DIR / "runepy.log"))
runepy_handler.setLevel(logging.INFO)

warnings_handler = logging.FileHandler(str(LOG_DIR / "warnings.log"))
warnings_handler.setLevel(logging.WARNING)

error_handler = logging.FileHandler(str(LOG_DIR / "errors.log"))
error_handler.setLevel(logging.ERROR)

handlers = [runepy_handler, warnings_handler, error_handler]

logging.basicConfig(level=logging.INFO, format=FORMAT, handlers=handlers)
logging.captureWarnings(True)
