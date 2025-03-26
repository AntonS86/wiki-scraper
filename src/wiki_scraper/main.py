from wiki_scraper.crawler import (
    crawl_vehicle_pages,
    crawl_wikipedia,
    create_queue_links,
)
from wiki_scraper.logger import logger
from wiki_scraper.storage import clear_vehicles_tables, init_db

if __name__ == "__main__":
    try:
        logger.info("Запуск программы")
        # инициализируем базу данных
        init_db()
        logger.info("Поиск и скачивание страниц с транспортными средствами")
        # добавляем в очередь начальную страницу
        create_queue_links()
        # запускаем процесс обхода
        crawl_wikipedia(MAX_PAGES=100000)
        # запускаем процесс парсинга страниц с транспортными средствами
        logger.info("Запуск парсинга страниц с транспортными средствами")
        # Очищаем данные из таблиц относящихся к автомобилям
        clear_vehicles_tables()
        # запуск парсинга html
        crawl_vehicle_pages()
        logger.info("Завершение программы")
    except Exception as e:
        logger.error(f"Ошибка: {e}: b1f785e6-007c-43cf-856e-ca1e270ffe44")
