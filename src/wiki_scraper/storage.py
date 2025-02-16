import sqlite3

from wiki_scraper.config import DB_FILE
from wiki_scraper.logger import logger


# Инициализация базы данных
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS pages (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   url TEXT UNIQUE,
                   title TEXT,
                   filepath TEXT,
                   category TEXT,
                   parsed INTEGER DEFAULT 0
                   )"""
    )
    conn.commit()
    conn.close()
    logger.info("База данных инициализирована.")


# Сохранение страницы в базу данных
def save_page(data):
    if not data:
        logger.warning("Попытка сохранить пустые данные! 9323e098-7cf3-405d-a654-5148892cff95")
        return

    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            """INSERT OR IGNORE INTO pages (
            url, title, filepath, category
            ) VALUES (?, ?, ?, ?)""",
            (data["url"], data["title"], data["filepath"], data["category"]),
        )
        conn.commit()
        logger.info(f"Данные сохранены: {data['url']}")
    except sqlite3.IntegrityError as e:
        logger.error(f"Ошибка целостности данных: {e}. b180040b-afce-4f11-b638-c2d337d4bc65")
        raise
    except sqlite3.OperationalError as e:
        logger.error(f"Ошибка операции с БД: {e}. b180040b-afce-4f11-b638-c2d337d4bc65")
        raise
    finally:
        if conn:
            conn.close()
