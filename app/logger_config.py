# app/logger_config.py

import logging
from datetime import datetime
from colorlog import ColoredFormatter

color_formatter = ColoredFormatter(
    fmt="%(log_color)s%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    log_colors={
        'DEBUG':    'cyan',
        'INFO':     'green',
        'WARNING':  'yellow',
        'ERROR':    'red',
        'CRITICAL': 'bold_red',
    }
)

console_handler = logging.StreamHandler()
console_handler.setFormatter(color_formatter)

file_handler = logging.FileHandler(
    filename=f'chatbot_logs_{datetime.now().strftime("%Y-%m-%d")}.log',
    encoding='utf-8'
)
file_formatter = logging.Formatter(
    fmt="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
file_handler.setFormatter(file_formatter)

logging.basicConfig(
    level=logging.INFO,
    handlers=[console_handler, file_handler]
)

logger = logging.getLogger("menedger.RUS")
