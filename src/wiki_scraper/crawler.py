import os
import random
import time

import requests

from wiki_scraper.config import HTML_PATH
from wiki_scraper.logger import logger
from wiki_scraper.scraper import parse_wikipedia_page
from wiki_scraper.storage import save_page

WIKI_BASE_URL = "https://en.wikipedia.org/wiki/"


# Сохраняет HTML содержимое страницы в файл
def save_html_to_file(page_data):
    try:
        # создаем все необходимые директории в пути к файлу, если их нет
        filepath = HTML_PATH / page_data["filepath"]
        os.makedirs(HTML_PATH, exist_ok=True)

        # открываем файл для записи в кодировке UTF-8
        with open(filepath, "w", encoding="utf-8") as f:
            # записываем HTML содержимое страницы в файл
            f.write(page_data["html"])

        logger.info(f"HTML сохранен в файл: {filepath}")
    except Exception as e:
        # логируем ошибку если что-то пошло не так при сохранении
        logger.error(f"Ошибка при сохранении HTML в файл {filepath}: {e}; 37a7bbc3-580d-4802-adb7-61bd6f75e188")
        raise


# обход страниц википедии начиная с указанного URL
def crawl_wikipedia(start_url):
    # множество для хранения посещенных URL
    visited_urls = set()

    # очередь URL для обхода
    # используем множество для очереди URL чтобы избежать дубликатов
    urls_queue = set()
    urls_queue.add(start_url)
    count = 0
    while urls_queue and count < 10:
        current_url = urls_queue.pop()
        count += 1
        # пропускаем если уже посещали
        if current_url in visited_urls:
            continue

        try:
            # получаем страницу
            response = requests.get(current_url)
            # Проверяет успешность HTTP запроса (код 200).
            # Если код ответа не 200,
            # выбрасывает исключение requests.exceptions.HTTPError
            response.raise_for_status()

            # парсим страницу
            page_data = parse_wikipedia_page(current_url, response.text)

            # сохраняем в БД
            save_page(page_data)

            # сохраняем HTML в файл
            save_html_to_file(page_data)

            # добавляем в посещенные только после
            # успешного сохранения в БД и файл
            visited_urls.add(current_url)

            # добавляем новые ссылки в очередь, только не посещенные
            urls_queue.update(link for link in page_data["links"] if link not in visited_urls)

            # задержка между запросами
            delay = random.uniform(1, 3)
            time.sleep(delay)

        except Exception as e:
            logger.error(f"Ошибка при обработке {current_url}: {e}; 3bb71c46-60bb-43d7-868b-81521e44001f")
            break
    print(urls_queue)
    print(visited_urls)
