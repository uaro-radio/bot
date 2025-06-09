import logging
import os
from logging.handlers import TimedRotatingFileHandler
log_dir = "Logs"
log_file = "Log.txt"
log_path = os.path.join(log_dir, log_file)

if not os.path.exists(log_dir):
    os.makedirs(log_dir)
if not os.path.exists(log_path):
    with open(log_path, "w") as f:
        f.write("Log file created.\n")

# Налаштування логу
#logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler(log_path)
file_handler.setFormatter(formatter)

# Консоль
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Список твоїх логгерів
loggers = {
    "UARO-Core": logging.getLogger("UARO-Core"),
    "UARO-SQLite": logging.getLogger("UARO-SQLite"),
    "UARO-ICS": logging.getLogger("UARO-ICS"),
    "UARO-IBS": logging.getLogger("UARO-IBS"),
    "httpx": logging.getLogger("httpx"),
    "telegram": logging.getLogger("telegram.ext.Application"),
    "UARO-SS": logging.getLogger("UARO-SS")
}

for logger in loggers.values():
    logger.setLevel(logging.INFO)
    logger.propagate = False  # <- це блокує дублювання з root-логгера
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

# Використання
Core_Log = loggers["UARO-Core"]
SQLite_Log = loggers["UARO-SQLite"]
ICS_Log = loggers["UARO-ICS"]
IBS_Log = loggers["UARO-IBS"]
SS_Log = loggers["UARO-SS"]