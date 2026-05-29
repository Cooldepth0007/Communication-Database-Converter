from __future__ import annotations

import logging
from pathlib import Path


def configure_logging(output_dir: Path | None = None) -> logging.Logger:
    log_dir = output_dir or Path.cwd()
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "Converter_Log.txt"

    logger = logging.getLogger("communication_database_converter")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    return logger
