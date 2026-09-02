import sys
import logging
from pathlib import Path
from backend.config import settings

def setup_logger(name: str = "resortvision") -> logging.Logger:
    logger = logging.getLogger(name)
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(log_level)

    if not logger.handlers:
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s] %(filename)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Console Handler
        c_handler = logging.StreamHandler(sys.stdout)
        c_handler.setFormatter(formatter)
        logger.addHandler(c_handler)

        # File Handler
        log_file = settings.LOGS_DIR / "resortvision.log"
        f_handler = logging.FileHandler(str(log_file), encoding="utf-8")
        f_handler.setFormatter(formatter)
        logger.addHandler(f_handler)

    return logger

logger = setup_logger("resortvision")
