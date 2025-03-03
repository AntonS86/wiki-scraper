import re
from typing import List
from urllib.parse import urljoin

from wiki_scraper.custom_types import Engine, Transmission
from wiki_scraper.data.countries import countries
from wiki_scraper.data.transmissions import transmissions


# очищаем url от параметров
# https://en.wikipedia.org/wiki/Toyota_Camry#V30_(1990%E2%80%931994) ->
#  Toyota_Camry
def clean_wiki_url(url):
    return url.split("/")[-1].split("#")[0].split("?")[0]


# преобразуем url в путь к файлу
# https://en.wikipedia.org/wiki/Toyota_Camry#V30_(1990%E2%80%931994)
# -> Toyota_Camry.html
def url_to_filepath(url):
    return clean_wiki_url(url) + ".html"


# шаблоны для классификации по категориям
patterns = {
    "list_of_vehicles_manufacturers1": re.compile(
        r"List_of_(?:the_)?[-\w]*?(automobile_manufacturers|car_brands|vehicles|automobiles|cars)"
    ),
    "list_of_vehicles_manufacturers2": re.compile(
        r"^List_of_(?:car|defunct_car|automobile|defunct_automobile)_manufacturers_(?:of|in|by)_(?:the_)?[-\w]+?$"
    ),
    "list_of_vehicles_industry1": re.compile(r"^Automotive_industry_(?:of|in|by)_(?:the_)?[-\w]+?$"),
    "list_of_vehicles_sales1": re.compile(
        r"^List_of_(?:automobile|truck|bus|motorcycle|scooter|bicycle)_sales_(?:of|in|by)_(?:the_)?[-\w]+?$"
    ),
}


# классифицируем страницу по url
def classify_page_by_url(url):
    for category, pattern in patterns.items():
        if pattern.match(url):
            return category
    return None


# ключевые слова для классификации по содержимому
content_keywords = {
    "company": [
        "company type",
        "industry",
        "founded",
        "founder",
        "headquarters",
        "employees",
        "subsidiaries",
    ],
    "car": [
        "manufacturer",
        "production",
        "model years",
        "body style",
        "engine",
        "power output",
        "transmission",
    ],
}


# классифицируем страницу по содержимому
def classify_page_by_content(soup):
    # Ищем все инфобоксы на странице
    infoboxes = soup.find_all("table", class_="infobox")

    for infobox in infoboxes:
        # Получаем текст инфобокса и приводим его к нижнему регистру
        text = infobox.get_text().lower()

        # Проверяем наличие ключевых слов для каждой категории
        for category, keywords in content_keywords.items():
            if any(keyword in text for keyword in keywords):
                return category

    return None


def classify_page(url, soup):
    url_category = classify_page_by_url(url)
    content_category = classify_page_by_content(soup)
    return url_category or content_category or "unknown"


# базовый url википедии
WIKI_BASE_URL = "https://en.wikipedia.org/wiki/"

# шаблоны для обработки ссылок
file_pattern = re.compile(r"\.(jpg|png|pdf|jpeg|gif)(\?.*)?(#.*)?$")
exclude_links_pattern = re.compile(
    r"/Special:|/Talk:|/Wikipedia:|/Help:|/Template:|/Template_talk:|/File:|/Main_Page|/Portal:|/Category"
)


# Собираем ссылки только внутри Википедии и очишаем их от параметров
def get_wiki_links(soup):
    s = set()
    links = soup.select("a[href^='/wiki/']")
    for link in links:
        href = link.get("href")
        if href and not file_pattern.search(href) and not exclude_links_pattern.search(href):
            full_url = urljoin(WIKI_BASE_URL, clean_wiki_url(href))
            s.add(full_url)
    return s


# исключаемые теги и классы
excluded_tags = [
    "script",
    "style",
    "noscript",
    "iframe",
    "img",
    "meta",
    "nav",
    "link",
]
exluded_classes = [
    "reflist",
    "references",
    "citation",
    "mw-references-wrap",  # Источники
    "sidebar",  # Боковые панели
    "vector-header-container",
    "wm-header",  # Заголовок
    "mw-editsection",
    "mw-hidden-catlinks",  # Примечания
    "external",
    "thumb",  # Внешние ссылки и изображения
    "mw-portlet",  # различные элементы внутри контента
    "vector-column-start",
    "vector-column-end",
    "vector-page-toolbar",
    "mw-footer-container",
    "vector-body-before-content",
    "vector-settings",
]


# Удаляем ненужные теги и элименты с классы для уменьшения размера html
def clean_html(soup):
    for tag in soup(excluded_tags):
        tag.decompose()

    for class_name in exluded_classes:
        for tag in soup.find_all(class_=class_name):
            tag.decompose()

    return soup


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


# шаблон для поиска годов производства
years_pattern = re.compile(r"\d{4}")


def parse_years_range(years_str: str | None):
    """
    Извлекает минимальный и максимальный год производства из строки.
    Если указан 'present', максимальный год становится None.
    """
    if years_str is None:
        return None, None

    years = years_pattern.findall(years_str)  # Находим все 4-значные числа (года)

    if not years:
        return None, None  # Если годов нет, вернуть None

    years = list(map(int, years))  # Преобразуем года в числа
    min_year = min(years)  # Самый ранний год
    max_year = max(years) if "present" not in years_str else None  # Самый поздний или None

    return min_year, max_year


# шаблон для поиска стран сборки автомобилей
country_patterns = re.compile(r"(?:^|/|(?:;\s)|(?:,\s)|(?:\)\s))([a-zA-Z\s]+?)(?=,|:|/|;|$)")


def parse_assembly_countries(text: str | None) -> List[str]:
    """
    Парсит страны сборки автомобилей из текста
    """

    if text is None:
        return []
    words: list[str] = country_patterns.findall(text)
    return [countries.get(word, "") for word in words if word in countries]


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
fuel_type_patern = re.compile(r"(?:hybrid )?(?:gasoline|petrol|diesel|electric)(?: hybrid)?")
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
            "type_fuel": "gasoline",
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

        # поиск типа топлива
        fuel_match = fuel_type_patern.search(el)
        if fuel_match:
            engine["type_fuel"] = fuel_match.group()
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
            "type_fuel": "electric",
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


speed_pattern = re.compile(r"\b(\d+)(?:-| )(?:speed|gear)\b")
transmisison_patern = re.compile(
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

        speed_match = speed_pattern.search(el)
        if speed_match:
            transmission["speed"] = int(speed_match.group(1))

        type_match = transmisison_patern.search(el)
        if type_match:
            transmission["type"] = transmissions.get(type_match.group(1))

        l_transmission.append(transmission)
    return l_transmission


class_sub_patern = re.compile(r"\s*\((?![A-Z]\b)[^)]*\)")


def parse_class(text: str | None) -> str | None:
    """
    Очищаем класс автомобиля от лишних данных
    """
    if text is None:
        return None
    return class_sub_patern.sub("", text).strip()


body_style_sub_patern = re.compile(r"\s*\([^)]*\)")


def parse_body_style(text: str | None) -> str | None:
    """
    Очищаем тип кузова автомобиля от лишних данных
    """
    if text is None:
        return None
    return body_style_sub_patern.sub("", text).strip()


def layout_parse(text: str | None) -> str | None:
    """
    Парсит информацию о расположении двигателя из текста
    """
    return parse_body_style(text)


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
