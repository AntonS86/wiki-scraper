import re
from urllib.parse import urljoin


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
