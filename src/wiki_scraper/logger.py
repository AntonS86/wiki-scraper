import logging
import sys

from wiki_scraper.config import LOG_FILE

# Создание логгера
logger = logging.getLogger("WikiCrawler")
logger.setLevel(logging.DEBUG)  # Уровень логирования

# Формат сообщений
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

# Вывод в файл
file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)  # Логировать всё в файл

# Вывод в консоль
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)  # В консоль логируем только INFO и выше

# Добавляем обработчики в логгер
logger.addHandler(file_handler)
logger.addHandler(console_handler)
