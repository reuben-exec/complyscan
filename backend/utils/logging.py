"""Utility helpers."""
import logging
from pathlib import Path


def setup_logging(name: str = "complyscan") -> logging.Logger:
    """Set up logging for the application."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(handler)
    
    return logger


logger = setup_logging()