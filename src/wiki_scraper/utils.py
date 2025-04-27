import re
import unicodedata
from typing import List
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from wiki_scraper.custom_types import Engine, ListClassifyPattern, Transmission
from wiki_scraper.data.body_style_patterns import body_style_patterns
from wiki_scraper.data.fuel_types import fuel_types
from wiki_scraper.data.layout_patterns import classify_layout
from wiki_scraper.data.transmissions import transmissions

# базовый url википедии
WIKI_BASE_URL = "https://en.wikipedia.org/wiki/"


def clean_url(url: str) -> str:
    """
    Очищает ссылку от параметров # и ?
    """
    return url.split("#")[0].split("?")[0]


# очищаем url от параметров
# https://en.wikipedia.org/wiki/Toyota_Camry#V30_(1990%E2%80%931994) ->
#  Toyota_Camry
def clean_wiki_url(url: str) -> str:
    return url.split("/")[-1].split("#")[0].split("?")[0]


# преобразуем url в путь к файлу
# https://en.wikipedia.org/wiki/Toyota_Camry#V30_(1990%E2%80%931994)
# -> Toyota_Camry.html
def url_to_filepath(url: str) -> str:
    return clean_wiki_url(url) + ".html"


def find_canonical_url(text: str) -> str | None:
    """Поиск канонического url на странице"""
    soup = BeautifulSoup(text, "html.parser")
    canonical = soup.find("link", {"rel": "canonical"})
    if isinstance(canonical, Tag):
        href = canonical.get("href")
        if isinstance(href, str):
            return clean_url(href)
    return None


# шаблоны для классификации по категориям
patterns = {
    "list_of_automobile_manufacturers": re.compile(r"^List_of_automobile_manufacturers$"),
    "list_of_company_vehicle": re.compile(r"^List_of(?:_[A-Za-z-]+)+_(?:vehicles|cars)$"),
}


# классифицируем страницу по url
def classify_page_by_url(url: str) -> str | None:
    for category, pattern in patterns.items():
        if pattern.match(url):
            return category
    return None


# ключевые слова для классификации по содержимому
content_keywords = {
    "company": {
        "company type",
        "industry",
        "founded",
        "headquarters",
    },
    "vehicle": {
        "manufacturer",
        "production",
        "model code",
        "class",
        "assembly",
        "body style",
        "layout",
        "engine",
        "transmission",
        "wheelbase",
    },
}


def classify_page_by_content(soup: Tag):
    """
    Классификация страницы по содержимому
    """
    th_list = {th.get_text().lower() for th in soup.select(".infobox th")}  # Используем set для быстрого поиска

    # Находим пересечение ключевых слов
    best_match = None
    max_score = 0

    for category, keywords in content_keywords.items():
        score = len(th_list & keywords)  # Количество совпадений
        if score > max_score:  # Запоминаем наилучшую категорию
            max_score = score
            best_match = category

    return best_match if max_score > 3 else None


def classify_page(url: str, soup: Tag) -> str:
    url_category = classify_page_by_url(url)
    content_category = classify_page_by_content(soup)
    return url_category or content_category or "unknown"


# шаблоны для обработки ссылок
file_href_pattern = re.compile(r"\.(jpg|png|pdf|jpeg|gif)(\?.*)?(#.*)?$")
exclude_href_pattern = re.compile(
    r"/Special:|/Talk:|/Wikipedia:|/Help:|/Template:|/Template_talk:|/File:|/Main_Page|/Portal:|/Category|/MOS:|/Aurion:"  # noqa E501
)

# исключаемые теги и классы
excluded_tags = ["script", "style", "iframe", "svg", "form", "input", "button"]
exluded_classes = [
    "sidebar",  # Боковые панели
    "nav",
    "footer",
    "ad",
    "ads",
    "banner",
    "social",
    "breadcrumb",
    "cookie" "reflist",
    "references",
    "citation",
    "mw-references-wrap",  # Источники
    "vector-header-container",
    "wm-header",  # Заголовок
    "mw-editsection",
    "mw-hidden-catlinks",  # Примечания
    "external",
    "thumb",  # Внешние ссылки и изображения
    "mw-portlet",  # различные элементы внутри контента
]


# Удаляем ненужные теги и элементы с классы для уменьшения размера html
def clean_html(soup: Tag) -> Tag:
    for tag in soup(excluded_tags):
        tag.decompose()

    # удаление ссылок над строками
    links = soup.find_all("sup", class_="reference")
    for link in links:
        link.decompose()

    for class_name in exluded_classes:
        for tag in soup.find_all(class_=class_name):
            tag.decompose()

    return soup


# ------------------ поиск ссылок на странице ------------------
# паттерн ссылки любые списки на на странице
list_of_href_pattern = re.compile(r"/Lists?_of")


def find_link_for_table(soup: Tag) -> set[str]:
    """Поиск ссылок в таблицах в низу страницы"""
    urls: set[str] = set()
    # ключевые слова для поиска ссылок
    key_words = ["cars", "models", "vehicles", "trucks", "vans", "suvs"]
    trs = soup.select("table.navbox-inner tr")
    for tr in trs:
        th = tr.find("th")
        if th:
            text = th.get_text(" ", strip=True).lower()
            if any(word in text for word in key_words):
                links = tr.select("a[href^='/wiki/']")
                for link in links:
                    href = link.get("href")
                    if (
                        isinstance(href, str)
                        and not file_href_pattern.search(href)
                        and not exclude_href_pattern.search(href)
                    ):
                        full_url = urljoin(WIKI_BASE_URL, clean_wiki_url(href))
                        urls.add(full_url)
    return urls


def find_links_by_list_of_automobile_manufacturers(soup: Tag) -> list[str]:
    """Поиск ссылок на страницы с производителями автомобилей"""
    urls: set[str] = set()
    links = soup.select("#bodyContent ul li a[href^='/wiki/']")
    for link in links:
        href = link.get("href")
        if (
            isinstance(href, str)
            and not file_href_pattern.search(href)
            and not exclude_href_pattern.search(href)
            and not list_of_href_pattern.search(href)
        ):
            full_url = urljoin(WIKI_BASE_URL, clean_wiki_url(href))
            urls.add(full_url)
    return list(urls)


def find_links_by_list_of_company_vehicle(soup: Tag) -> list[str]:
    """Поиск ссылок на страницы с автомобилями компаний"""
    urls: set[str] = set()
    links = soup.select("#bodyContent table.wikitable th a[href^='/wiki/'], #bodyContent ul li a[href^='/wiki/']")
    for link in links:
        href = link.get("href")
        if (
            isinstance(href, str)
            and not file_href_pattern.search(href)
            and not exclude_href_pattern.search(href)
            and not list_of_href_pattern.search(href)
        ):
            full_url = urljoin(WIKI_BASE_URL, clean_wiki_url(href))
            urls.add(full_url)
    return list(urls)


def find_links_by_vehicle(soup: Tag) -> list[str]:
    """Поиск ссылок на страницы с автомобилями"""
    urls: set[str] = set()
    links: list[Tag] = list()

    # поиск ссылок в колонках infobox
    trs = soup.select(".infobox tr")
    for tr in trs:
        th = tr.find("th")
        if th is not None and th.get_text(strip=True).lower() in ["predecessor", "successor", "related"]:
            links += tr.select("td a[href^='/wiki/']")

    # поиск ссылок в тексте, main article, see also
    links += soup.select("#bodyContent .hatnote a[href^='/wiki/']")

    for link in links:
        href = link.get("href")
        if isinstance(href, str) and not file_href_pattern.search(href) and not exclude_href_pattern.search(href):
            full_url = urljoin(WIKI_BASE_URL, clean_wiki_url(href))
            urls.add(full_url)
    # объединяем ссылки из таблиц и текста
    urls |= find_link_for_table(soup)
    return list(urls)


list_of_vehicles_pattern = re.compile(r"^/wiki/List_of(?:_[A-Za-z-]+)+_(?:vehicles|cars)$")


def find_links_by_company(soup: Tag) -> list[str]:
    """Поиск ссылок на страницы с компаниями"""
    urls: set[str] = set()
    links = soup.select("#bodyContent a[href^='/wiki/']")
    for link in links:
        href = link.get("href")
        if isinstance(href, str) and list_of_vehicles_pattern.search(href):
            full_url = urljoin(WIKI_BASE_URL, clean_wiki_url(href))
            urls.add(full_url)

    # объединяем ссылки из таблиц и текста
    urls |= find_link_for_table(soup)
    return list(urls)


def find_links_by_category_page(category: str, soup: Tag) -> list[str]:
    """Поиск ссылок на страницы по категориям страницы"""
    if category == "list_of_automobile_manufacturers":
        return find_links_by_list_of_automobile_manufacturers(soup)
    if category == "list_of_company_vehicle":
        return find_links_by_list_of_company_vehicle(soup)
    if category == "vehicle":
        return find_links_by_vehicle(soup)
    if category == "company":
        return find_links_by_company(soup)
    return []


# ------------------ парсинг данных из инфобокса ------------------


def classify(text: str, body_classes: ListClassifyPattern) -> str:
    """
    Классифицирует текст на основе заданных категорий.
    """
    text_words = set(text.split())  # Разбиваем текст на слова
    best_match = "unknown"
    best_score = 0

    for category in body_classes:
        words = set(category["words"])  # Преобразуем слова категории в множество
        score = len(words & text_words)  # Считаем количество совпадений

        if score > best_score:  # Если нашли категорию с большим совпадением
            best_match = category["category"]
            best_score = score

    return best_match


def remove_diacritics(text: str) -> str:
    """Удаляет диакритические знаки из текста"""
    # Нормализуем строку в форму NFKD
    normalized_text = unicodedata.normalize("NFKD", text)
    # Убираем символы, которые являются диакритическими знаками
    cleaned_text = "".join(char for char in normalized_text if not unicodedata.combining(char))
    return cleaned_text


def str_to_column_name(str):
    """преобразуем строку в имя колонки"""
    return str.lower().replace(" ", "_")


def create_model_name(page_title, infobox_title):
    """
    создаем имя модели

    объединяем имя модели и под тип или поколение, по аналогии с википедией

    """
    if all(word in infobox_title for word in page_title.split(" ")):
        return infobox_title
    else:
        return f"{page_title} ({infobox_title})"


# шаблон для поиска производителей автомобилей
manufacture_patterns = re.compile(r"[A-Z][A-Za-z]+(?:[ \-][A-Z][A-Za-z]+)*")


def parse_manufacturer_company(text: str | None) -> List[str]:
    """
    Парсит компании сборки автомобилей из текста
    """
    if text is None:
        return []
    return manufacture_patterns.findall(text)


volume_l_pattern = re.compile(r"\b(\d+(?:\.\d+)?) ?l\b")
volume_cc_pattern = re.compile(r"\b(\d+(?:,\d+)?) ?cc\b")
fuel_type_pattern = re.compile(r"(?:hybrid )?(?:gasoline|petrol|diesel|electric)(?: hybrid)?")
power_pattern = re.compile(r"\b(\d+(?:\.\d+)?)\s?(?:hp|horsepower)\b")


def parse_engine(text: str | None) -> List[Engine]:
    """
    Парсит информацию о двигателях из текста
    """

    if text is None:
        return []

    text_split = [t.strip() for t in text.lower().split(";")]

    l_engine: List[Engine] = []
    for i, el in enumerate(text_split):
        engine: Engine = {
            "text": el,
            "volume": None,
            "type_fuel": fuel_types.get("petrol"),
            "power": None,
        }
        # поиск объема двигателя
        volume: float | None = None
        cc_match = volume_cc_pattern.search(el)
        if cc_match:
            volume = round(float(cc_match.group(1).replace(",", "")) / 1000, 1)
        else:
            volume_match = volume_l_pattern.search(el)
            if volume_match:
                volume = float(volume_match.group(1))
        engine["volume"] = volume

        # поиск типа топлива
        fuel_match = fuel_type_pattern.search(el)
        if fuel_match:
            engine["type_fuel"] = fuel_types.get(fuel_match.group())
        else:
            if i != 0:
                engine["type_fuel"] = l_engine[i - 1].get("type_fuel")

        # поиск мощности
        p_match = power_pattern.search(el, re.IGNORECASE)
        if p_match:
            engine["power"] = float(p_match.group(1))

        l_engine.append(engine)
    return [t for t in l_engine if t["volume"] is not None or t["power"] is not None]


def parse_electric_engine(text: str | None) -> List[Engine]:
    """
    Парсит информацию о электрических двигателях из текста
    """

    if text is None:
        return []

    text_split = [t.strip() for t in text.lower().split(";")]

    l_engine: List[Engine] = []
    for i, el in enumerate(text_split):
        engine: Engine = {
            "text": el,
            "volume": None,
            "type_fuel": fuel_types.get("electric"),
            "power": None,
        }
        # поиск объема двигателя
        volume: float | None = None
        volume_match = volume_l_pattern.search(el)
        if volume_match:
            volume = float(volume_match.group(1))
        else:
            cc_match = volume_cc_pattern.search(el)
            if cc_match:
                volume = round(float(cc_match.group(1).replace(",", "")) / 1000, 1)
        engine["volume"] = volume

        # поиск мощности
        p_match = power_pattern.search(el, re.IGNORECASE)
        if p_match:
            engine["power"] = float(p_match.group(1))

        l_engine.append(engine)
    return l_engine


speed_group_pattern = re.compile(r"\b(\d+(?:[ -]*(?:/|or) ?\d+)*?)[ -]*(?:speed|spd|gear)\b")
speed_pattern = re.compile(r"\d+")
transmission_pattern = re.compile(
    r"\b(ecvt|cvt|dct|amt|smt|at|mt|ev|dsg|hst|hydrostatic|direct|electric|dual|continuously|tiptronic|sequential|manual|automatic|automated)\b"  # noqa E501
)


def parse_transmission(text: str | None) -> List[Transmission]:
    """
    Парсит информацию о трансмиссии из текста
    """
    if text is None:
        return []
    text_split = [t.strip() for t in text.lower().split(";")]
    l_transmission: List[Transmission] = []
    for el in text_split:
        transmission: Transmission = {
            "text": el,
            "type": None,
            "speed": None,
        }

        type_match = transmission_pattern.search(el)
        if type_match:
            transmission["type"] = transmissions.get(type_match.group(1))

        # поиск количества скоростей, при паттерне 3/4-speed
        # создаем объект на каждую скорость
        speed_match = speed_group_pattern.search(el)
        if speed_match:
            speed_group = speed_match.group(1)
            list_num = speed_pattern.findall(speed_group)
            for el in list_num:
                t: Transmission = {**transmission, "speed": int(el)}
                l_transmission.append(t)
        else:
            l_transmission.append(transmission)

    return l_transmission


# паттерны для поиска двойного разделителя
double_delimiter_pattern = re.compile(r";;")

# паттерны для замены разделителей
class_delimiter_pattern = re.compile(r"\s*(?:[,/]|and)\s*")

class_sub_pattern = re.compile(r"\s*\((?![A-Z]\b)[^)]*\)")


def parse_class(text: str | None) -> str | None:
    """
    Очищаем класс автомобиля от лишних данных
    """
    if text is None:
        return None
    text = class_sub_pattern.sub("", text)
    text = class_delimiter_pattern.sub(";", text)
    text = double_delimiter_pattern.sub(";", text)
    return text.lower().strip()


body_minus_pattern = re.compile(r"-(?=/)")
body_delimiter_pattern = re.compile(r"(?<=[^\d])\s*(?:[,/]|and|or)\s*")
# поиск данных в скобках
body_style_sub_pattern = re.compile(r"\s*\([^)]*\)")
# поиск не словесных символов
not_word_char_pattern = re.compile(r"[^\w]")
# поиск двойных пробелов
group_space_pattern = re.compile(r"\s{2,}")


def parse_body_style(text: str | None) -> str | None:
    """
    Очищаем тип кузова автомобиля от лишних данных
    """
    if text is None:
        return None
    cats: set[str] = set()
    for part in text.split(";"):
        part = part.lower().strip()
        # заменяем не словесные символы пробелами
        part = not_word_char_pattern.sub(" ", part)
        # удаляем лишние пробелы
        part = group_space_pattern.sub(" ", part)
        cats.add(classify(part, body_style_patterns))
    return ";".join(cats)


def layout_parse(text: str | None) -> str | None:
    """
    Парсит информацию о расположении двигателя из текста
    """
    if text is None:
        return None
    text = double_delimiter_pattern.sub(";", text)
    cats: set[str] = set()
    for part in text.split(";"):
        cats |= classify_layout(part)
    return ";".join(cats)


millimeters_pattern = re.compile(r"\b(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s?mm\b")


def find_max_millimeters(text: str | None) -> float | None:
    """
    Находит максимальное значение в миллиметрах в текст
    """
    if text is None:
        return None
    all = millimeters_pattern.findall(text)
    millimeters = list(map(lambda x: float(x.replace(",", "")), all))
    return max(millimeters) if millimeters else None


meters_pattern = re.compile(r"\b(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s?(?:metres|m)\b")


def find_max_meters(text: str | None) -> float | None:
    """
    Находит максимальное значение в метрах в текст
    """
    if text is None:
        return None
    all = meters_pattern.findall(text)
    meters = list(map(lambda x: float(x.replace(",", "")), all))
    return max(meters) if meters else None


def parse_meters(text: str | None) -> float | None:
    """
    Парсит длину в метрах
    """
    mm = find_max_millimeters(text)
    if mm is not None:
        return mm / 1000
    return find_max_meters(text)


kilograms_pattern = re.compile(r"\b(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s?kg\b")


def parse_kilogrames(text: str | None) -> float | None:
    """
    Парсит вес в килограммах
    """
    if text is None:
        return None
    all = kilograms_pattern.findall(text)
    kilogrames = list(map(lambda x: float(x.replace(",", "")), all))
    return max(kilogrames) if kilogrames else None
