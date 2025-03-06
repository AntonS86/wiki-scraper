from wiki_scraper.crawler import crawl_vehicle_pages, crawl_wikipedia
from wiki_scraper.logger import logger
from wiki_scraper.storage import add_to_queue, init_db

ROOT_URL = "https://en.wikipedia.org/wiki/List_of_automobile_manufacturers"

if __name__ == "__main__":
    try:
        logger.info("Запуск программы")
        # инициализируем базу данных
        init_db()
        logger.info("Запуск скачивания страниц")
        # добавляем в очередь начальную страницу
        add_to_queue(ROOT_URL, priority=1)
        # добавил списки авто для ускорения парсинга
        # add_new_links_to_queue(
        #     [
        #         "https://en.wikipedia.org/wiki/Toyota_Corolla_(E10)",
        #     ]
        # )
        logger.info("Поиск и скачивание страниц с транспортными средствами")
        # запускаем процесс обхода
        crawl_wikipedia(MAX_PAGES=10000)
        # запускаем процесс парсинга страниц с транспортными средствами
        logger.info("Запуск парсинга страниц с транспортными средствами")
        crawl_vehicle_pages()
        logger.info("Завершение программы")
    except Exception as e:
        logger.error(f"Ошибка: {e}: b1f785e6-007c-43cf-856e-ca1e270ffe44")
