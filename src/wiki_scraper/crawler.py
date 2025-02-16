import os
import random
import time

import requests

from wiki_scraper.config import HTML_PATH
from wiki_scraper.logger import logger
from wiki_scraper.scraper import parse_wikipedia_page
from wiki_scraper.storage import (
    add_new_links_to_queue,
    get_next_url,
    is_visited,
    mark_as_visited,
    save_page,
)

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


# заголовки для запроса
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}


# обход страниц википедии начиная с указанного URL
def crawl_wikipedia(MAX_PAGES=100):
    # счетчик ошибок соединения
    connection_error_count = 0
    # счетчик пройденных страниц
    count = 0
    while count < MAX_PAGES:
        try:
            current_url = get_next_url()
            count += 1

            if not current_url:
                logger.info("Очередь пуста, завершение работы")
                break

            # пропускаем если уже посещали
            if is_visited(current_url):
                continue

            # получаем страницу
            response = requests.get(current_url, headers=headers)
            # Проверяет успешность HTTP запроса (код 200).
            # Если код ответа не 200,
            # выбрасывает исключение requests.exceptions.HTTPError
            response.raise_for_status()
            # обнуляем ошибку соединения
            connection_error_count = 0

            # парсим страницу
            page_data = parse_wikipedia_page(current_url, response.text)

            # сохраняем в БД
            save_page(page_data)

            # сохраняем HTML в файл
            save_html_to_file(page_data)

            # добавляем новые ссылки в очередь, только не посещенные
            add_new_links_to_queue([link for link in page_data["links"] if not is_visited(link)])

            # добавляем в посещенные только после
            # успешного сохранения в БД и файл
            mark_as_visited(current_url)

            # задержка между запросами
            time.sleep(random.uniform(1, 3))

        except requests.exceptions.HTTPError as e:
            # обработка некоторых кодов ошибок
            if response.status_code == 429:
                logger.warning(f"Ошибка HTTP: слишком много запросов, {e}; f4e66669-ecc1-498e-a71d-384715cb3ec7")
                time.sleep(random.uniform(5, 15))
                continue
            logger.error(f"Ошибка HTTP: {e}; 36b8564d-a09c-4420-bf2d-d5ed93acaaac")
            break

        except requests.exceptions.ConnectionError:
            if connection_error_count > 20:
                logger.error(
                    f"Ошибка соединения. Не смогли подключиться больше {connection_error_count} раз."
                    f"dc89e030-8753-4f57-9d2a-4be5c3fcf10c"
                )
                break
            logger.warning("Ошибка соединения. Проверяем интернет и пробуем снова...")
            connection_error_count += 1
            time.sleep(10)
            continue

        except Exception as e:
            logger.error(f"Ошибка при обработке {current_url}: {e}; 3bb71c46-60bb-43d7-868b-81521e44001f")
            break
