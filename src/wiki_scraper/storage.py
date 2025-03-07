import sqlite3

from wiki_scraper.config import DB_FILE
from wiki_scraper.custom_types import Vehicle
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
                    model_code TEXT,
                    production_start_year INTEGER,
                    production_end_year INTEGER,
                    vehicle_class TEXT,
                    body_style TEXT,
                    layout TEXT,
                    wheelbase REAL,
                    length REAL,
                    width REAL,
                    height REAL,
                    weight REAL,
                    json TEXT,
                    UNIQUE (url, model_name)
                );
            """
            )

            # создание таблицы для хранения данных о двигателе
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS engines (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    vehicle_id INTEGER NOT NULL,
                    text TEXT,
                    type_fuel TEXT,
                    volume REAL,
                    power REAL
                );
            """
            )

            # создание таблицы для хранения данных о коробке передач
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS transmissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    vehicle_id INTEGER NOT NULL,
                    text TEXT,
                    type TEXT,
                    speed INTEGER
                );
            """
            )

            # создание таблицы для хранения данных о странах сборки
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS assemblies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    vehicle_id INTEGER NOT NULL,
                    country TEXT,
                    UNIQUE (vehicle_id, country)
                );
            """
            )

            # создание таблицы для хранения данных о производителях
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS manufacturers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    vehicle_id INTEGER NOT NULL,
                    company TEXT,
                    UNIQUE (vehicle_id, company)
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


def add_vehicle(data: Vehicle):
    """Добавляет транспортное средство в базу данных"""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            # вставляем автомобиль в таблицу vehicles
            cursor.execute(
                """
                    INSERT OR IGNORE INTO vehicles (
                    url,
                    filepath,
                    model_name,
                    model_code,
                    production_start_year,
                    production_end_year,
                    vehicle_class,
                    body_style,
                    layout,
                    wheelbase,
                    length,
                    width,
                    height,
                    weight,
                    json
                    ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?
                    )""",
                (
                    data["url"],
                    data["filepath"],
                    data["model_name"],
                    data["model_code"],
                    data["production_start_year"],
                    data["production_end_year"],
                    data["vehicle_class"],
                    data["body_style"],
                    data["layout"],
                    data["wheelbase"],
                    data["length"],
                    data["width"],
                    data["height"],
                    data["weight"],
                    data["json"],
                ),
            )

            # получаем id добавленного автомобиля
            vehicle_id = cursor.lastrowid
            # Если запись уже существовала, получаем ID вручную
            if vehicle_id is None:
                cursor.execute(
                    "SELECT id FROM vehicles WHERE url = ? and model_name = ?", (data["url"], data["model_name"])
                )
                result = cursor.fetchone()
                if not result:
                    return
                vehicle_id = result[0]

            # вставляем данные о двигателе
            for engine in data["engine_list"]:
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO engines (
                        vehicle_id,
                        text,
                        type_fuel,
                        volume,
                        power
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (vehicle_id, engine["text"], engine["type_fuel"], engine["volume"], engine["power"]),
                )

            # вставляем данные о коробке передач
            for transmission in data["transmission_list"]:
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO transmissions (
                        vehicle_id,
                        text,
                        type,
                        speed
                    ) VALUES (?, ?, ?, ?)
                    """,
                    (vehicle_id, transmission["text"], transmission["type"], transmission["speed"]),
                )

            # вставляем данные о странах сборки
            for country in data["assembly_list"]:
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO assemblies (
                        vehicle_id,
                        country
                    ) VALUES (?, ?)
                    """,
                    (vehicle_id, country),
                )

            # вставляем данные о производителях
            for company in data["manufacturer_list"]:
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO manufacturers (
                        vehicle_id,
                        company
                    ) VALUES (?, ?)
                    """,
                    (vehicle_id, company),
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
                cursor.execute("SELECT * FROM pages WHERE category = 'vehicle' LIMIT ? OFFSET ?", (batch_size, offset))
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
