import logging

# Configure loggers
FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
handlers = [
    logging.FileHandler("runepy.log"),
    logging.FileHandler("warnings.log"),
]
error_handler = logging.FileHandler("errors.log")
error_handler.setLevel(logging.ERROR)
handlers.append(error_handler)

logging.basicConfig(level=logging.INFO, format=FORMAT, handlers=handlers)
logging.captureWarnings(True)
