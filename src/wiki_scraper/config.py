import os
from pathlib import Path

from dotenv import load_dotenv

# Определяем корневую папку проекта (wiki/)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Загружаем .env
load_dotenv(BASE_DIR / ".env")

# Читаем переменные или задаем значения по умолчанию
DB_PATH = BASE_DIR / os.getenv("DB_PATH", "/db")
LOGS_PATH = BASE_DIR / os.getenv("LOGS_PATH", "/logs")
HTML_PATH = BASE_DIR / os.getenv("HTML_PATH", "/html")
CSV_PATH = BASE_DIR / os.getenv("CSV_PATH", "/csv")

LOG_FILE = LOGS_PATH / "wikicrawler.log"
DB_FILE = DB_PATH / "wikipedia.db"
# Проверяем, всё ли загружено
if __name__ == "__main__":  # Тестирование при запуске config.py
    print(f"BASE_DIR: {BASE_DIR}")
    print(f"Database: {DB_PATH}")
    print(f"Logs: {LOGS_PATH}")
    print(f"HTML: {HTML_PATH}")
    print(f"LOG_FILE: {LOG_FILE}")
    print(f"DB_FILE: {DB_FILE}")
    print(f"csv: {CSV_PATH}")
