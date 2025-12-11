# framework/utils/logger.py
import logging
from pathlib import Path
from datetime import datetime

LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

# 1 file log / 1 ngày: logs/test_20251210.log
LOG_FILE = LOG_DIR / f"test_{datetime.now().strftime('%Y%m%d')}.log"

def get_logger(name: str = "selenium"):
    """
    Trả về logger dùng chung cho framework.
    Nếu logger đã được cấu hình handler trước đó thì dùng lại, không add handler mới.
    """
    logger = logging.getLogger(name)

    # Nếu logger đã có handler rồi thì không cấu hình lại (tránh log bị nhân đôi)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    # Log ra console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Log ra file
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    # Không propagate lên root logger nữa, tránh log trùng
    logger.propagate = False

    return logger
