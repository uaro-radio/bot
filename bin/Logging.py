import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
# Системні логи
Core_Log = logging.getLogger("UARO-Core")
SQLite_Log = logging.getLogger("UARO-SQLite")

# Модульні логи
ICS_Log = logging.getLogger("UARO-ICS") # ICS - Information Correction System

