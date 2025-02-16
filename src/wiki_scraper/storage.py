import sqlite3

from wiki_scraper.config import DB_FILE
from wiki_scraper.logger import logger


def init_db():
    """Инициализация базы данных"""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            # Создание таблицы для сохраненых страниц
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

            # Создание таблицы для посещенных страниц
            cursor.execute(
                """CREATE TABLE IF NOT EXISTS visited (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT UNIQUE NOT NULL,
                    visited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )"""
            )

            # Создание таблицы для очереди посещения страниц
            cursor.execute(
                """CREATE TABLE IF NOT EXISTS queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT UNIQUE NOT NULL,
                    priority INTEGER DEFAULT 0
                )"""
            )

            conn.commit()

            logger.info("База данных инициализирована.")
    except sqlite3.OperationalError as e:
        logger.error(f"Ошибка операции с БД: {e}. eacd40ac-a73d-46ce-b911-67b8d5b5028f")
        raise


def add_to_queue(url, priority=0):
    """Добавляет URL в очередь, если его там нет"""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO queue (url, priority) VALUES (?, ?)", (url, priority))
        conn.commit()
    except sqlite3.DatabaseError as e:
        logger.error(f"Ошибка добавления в очередь: {e}. 595c29ed-849c-4f15-8b1c-bbd776100579")
        raise


def get_next_url():
    """Получает следующий URL из очереди (сортировка по приоритету)"""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT url FROM queue ORDER BY priority DESC LIMIT 1")
            result = cursor.fetchone()
            if result:
                return result[0]
            return None
    except sqlite3.DatabaseError as e:
        logger.error(f"Ошибка получения URL из очереди: {e}. 5528cb13-64bd-4cb6-9fee-232568c06468")
        raise


def mark_as_visited(url):
    """Переносит URL из queue в visited"""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO visited (url) VALUES (?)", (url,))
            cursor.execute("DELETE FROM queue WHERE url = ?", (url,))
            conn.commit()
    except sqlite3.DatabaseError as e:
        logger.error(f"Ошибка переноса URL в visited: {e}. 6586c9a1-540e-46fb-beb3-d09277145676")
        raise


def is_visited(url):
    """Проверяет, посещалась ли уже эта ссылка"""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT EXISTS(SELECT 1 FROM visited WHERE url = ?)", (url,))
            return cursor.fetchone()[0] == 1
    except sqlite3.DatabaseError as e:
        logger.error(f"Ошибка проверки посещения ссылки: {e}. 8dd5ff15-d97e-40f3-85ff-691c47bea425")
        raise


def add_new_links_to_queue(links):
    """Добавляет новые найденные ссылки в очередь"""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.executemany("INSERT OR IGNORE INTO queue (url) VALUES (?)", [(link,) for link in links])
            conn.commit()
    except sqlite3.DatabaseError as e:
        logger.error(f"Ошибка добавления ссылок в очередь: {e}. 86b8629e-c885-4fdc-8660-beb0e9bd6c9d")
        raise


def save_page(data):
    """Сохраняет страницу в базу данных"""
    if not data:
        logger.warning("Попытка сохранить пустые данные! 9323e098-7cf3-405d-a654-5148892cff95")
        return
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT OR IGNORE INTO pages (
                url, title, filepath, category
                ) VALUES (?, ?, ?, ?)""",
                (data["url"], data["title"], data["filepath"], data["category"]),
            )
            conn.commit()
            logger.info(f"Данные сохранены: {data['url']}")
    except sqlite3.DatabaseError as e:
        logger.error(f"Ошибка сохранения страницы: {e}. b180040b-afce-4f11-b638-c2d337d4bc65")
        raise
