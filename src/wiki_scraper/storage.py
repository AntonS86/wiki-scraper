import json
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
                   url TEXT UNIQUE NOT NULL,
                   title TEXT,
                   filepath TEXT NOT NULL,
                   category TEXT
                   )"""
            )

            # Создание таблицы для подсчета количества парсинга страниц
            cursor.execute(
                """CREATE TABLE IF NOT EXISTS parsed (
                    url TEXT PRIMARY KEY,
                    parsed_count INTEGER DEFAULT 1,
                    last_parsed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

            # Создание таблицы для c транспортными средствами
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS vehicles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filepath TEXT NOT NULL,
                    url TEXT NOT NULL,
                    model_name TEXT,
                    also_called TEXT,
                    model_code TEXT,
                    production TEXT,
                    model_years TEXT,
                    assembly TEXT,
                    manufacturer TEXT,
                    class TEXT,
                    body_style TEXT,
                    platform TEXT,
                    engine TEXT,
                    electric_motor TEXT,
                    electric_range TEXT,
                    power_output TEXT,
                    transmission TEXT,
                    battery TEXT,
                    wheelbase TEXT,
                    layout TEXT,
                    length TEXT,
                    width TEXT,
                    height TEXT,
                    weight TEXT,
                    kerb_weight TEXT,
                    curb_weight TEXT,
                    json TEXT,
                    UNIQUE (url, model_name)
                );
            """
            )

            conn.commit()

            logger.info("База данных инициализирована.")
    except sqlite3.OperationalError as e:
        logger.error(f"Ошибка операции с БД: {e}. eacd40ac-a73d-46ce-b911-67b8d5b5028f")
        raise


def increment_parsed_count(url):
    """Увеличивает счетчик parsed для URL"""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO parsed (url, parsed_count)
            VALUES (?, 1)
            ON CONFLICT(url) DO UPDATE SET
                parsed_count = parsed_count + 1,
                last_parsed = CURRENT_TIMESTAMP
        """,
            (url,),
        )

        conn.commit()
    except sqlite3.DatabaseError as e:
        logger.error(f"Ошибка увеличения счетчика в таблице parsed: {e}. 3d272c8b-2acd-4e98-bf29-accdd60fd675")
        raise


def add_vehicle(data):
    """Добавляет транспортное средство в базу данных"""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            # храним json данные в отдельном поле
            cursor.execute(
                """
                           INSERT OR IGNORE INTO vehicles (
                           also_called,
                           assembly,
                           battery,
                           body_style,
                           class,
                           curb_weight,
                           electric_motor,
                           electric_range,
                           engine,
                           filepath,
                           height,
                           kerb_weight,
                           layout,
                           length,
                           manufacturer,
                           model_code,
                           model_name,
                           model_years,
                           platform,
                           power_output,
                           production,
                           transmission,
                           url,
                           weight,
                           wheelbase,
                           width,
                           json
                           ) VALUES (
                           ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                           ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                           ?, ?, ?, ?, ?, ?, ?
                           )""",
                (
                    data["also_called"],
                    data["assembly"],
                    data["battery"],
                    data["body_style"],
                    data["class"],
                    data["curb_weight"],
                    data["electric_motor"],
                    data["electric_range"],
                    data["engine"],
                    data["filepath"],
                    data["height"],
                    data["kerb_weight"],
                    data["layout"],
                    data["length"],
                    data["manufacturer"],
                    data["model_code"],
                    data["model_name"],
                    data["model_years"],
                    data["platform"],
                    data["power_output"],
                    data["production"],
                    data["transmission"],
                    data["url"],
                    data["weight"],
                    data["wheelbase"],
                    data["width"],
                    json.dumps(data),
                ),
            )
            conn.commit()
    except sqlite3.DatabaseError as e:
        logger.error(f"Ошибка добавления транспортного средства: {e}. 88353cb0-0e20-426d-b574-77da7404ac5a")
        raise


def get_car_pages_generator(batch_size=1000):
    """Генератор для построчного чтения данных"""

    offset = 0
    try:
        with sqlite3.connect(DB_FILE) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            while True:
                cursor.execute("SELECT * FROM pages WHERE category = 'car' LIMIT ? OFFSET ?", (batch_size, offset))
                rows = cursor.fetchall()
                # Если строк больше нет — выходим
                if not rows:
                    break

                # Возвращаем каждую строку по одной
                yield from rows
                offset += batch_size
    except sqlite3.DatabaseError as e:
        logger.error(f"Ошибка получения страниц: {e}. edcf1df0-364e-4545-9074-1fe1c9a262f6")
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
