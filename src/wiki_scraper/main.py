from wiki_scraper.crawler import crawl_wikipedia
from wiki_scraper.logger import logger
from wiki_scraper.storage import init_db

ROOT_URL = "https://en.wikipedia.org/wiki/List_of_automobile_manufacturers"

if __name__ == "__main__":
    try:
        logger.info("Запуск программы")
        init_db()
        crawl_wikipedia(ROOT_URL)
        logger.info("Завершение программы")
    except Exception as e:
        logger.error(f"Ошибка: {e}: b1f785e6-007c-43cf-856e-ca1e270ffe44")
