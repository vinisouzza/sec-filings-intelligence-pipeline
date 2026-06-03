import logging
from pathlib import Path

def get_logger():
    """Get a logger instance."""

    Path("data/logs").mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("pipeline")

    if logger.handlers:
        return logger
    
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    file_handler = logging.FileHandler("data/logs/pipeline.log")

    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger