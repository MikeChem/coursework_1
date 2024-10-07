import logging
import os
from typing import Any


def setup_logger(name: str, file_logs: str) -> Any:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    rel_file_path = os.path.join(current_dir, "../logs/utils.log")
    abs_file_path = os.path.abspath(rel_file_path)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(abs_file_path, mode="w")
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger
