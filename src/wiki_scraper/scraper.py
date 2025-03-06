import json
from typing import Dict, List

from bs4 import BeautifulSoup, Tag
from bs4.element import NavigableString

from wiki_scraper.custom_types import Vehicle
from wiki_scraper.utils import (
    classify_page,
    clean_html,
    clean_wiki_url,
    create_model_name,
    find_links_by_category_page,
    layout_parse,
    parse_assembly_countries,
    parse_body_style,
    parse_class,
    parse_electric_engine,
    parse_engine,
    parse_kilogrames,
    parse_manufacturer_company,
    parse_meters,
    parse_transmission,
    parse_years_range,
    str_to_column_name,
    url_to_filepath,
)


# парсинг страницы википедии и классификация по категориям
def parse_wikipedia_page(url, response_text):
    # путь к файлу
    filepath = url_to_filepath(url)

    soup: Tag = BeautifulSoup(response_text, "html.parser")

    # очищаем страницу от скриптов, картинок, стилей и т.д.
    soup = clean_html(soup)

    # поиск заголовка страницы
    page_title = soup.find("h1", class_="mw-first-heading")
    title = page_title.get_text() if page_title else ""

    # классификация по содержимому
    category = classify_page(clean_wiki_url(url), soup)

    # получаем ссылки на страницы внутри википедии
    links = find_links_by_category_page(category, soup)

    html = str(soup)

    return {
        "url": url,
        "title": title,
        "category": category,
        "filepath": filepath,
        "html": html,
        "links": links,
    }


# Функция для очистки текста
def clean_text(text: str, default="N/A"):
    """
    Очищает текст: удаляет лишние пробелы, заменяет \xa0 на пробелы
    и возвращает значение по умолчанию, если текст пустой.
    """
    if text is None:
        return default
    cleaned_text = text.replace("\xa0", " ").replace(";", ",").strip()
    return cleaned_text if cleaned_text else default


def clean_cell(cell: Tag):
    """обработка и извлечение текста из ячейки"""

    # обработка td
    # поиск списков
    lis = cell.find_all("li")
    if len(lis) > 0:
        lst = [clean_text(li.text) for li in lis]
        return ";".join(lst)

    # поиск списков с разделителями <br>
    brs = cell.find_all("br")
    if len(brs) > 0:
        # замена <br> на строковый разделитель
        for br in brs:
            br.replace_with(NavigableString("#br#"))
        lst = [clean_text(li) for li in cell.get_text(strip=True).split("#br#")]
        return ";".join(lst)

    # в остальных случаях
    return clean_text(cell.text)


def parse_vehicle_page(url, response_text):
    """парсинг страницы с техникой"""
    soup = BeautifulSoup(response_text, "html.parser")

    title_element = soup.find("h1", class_="firstHeading")
    title = title_element.get_text() if title_element else ""

    # удаление ссылок над строками
    links = soup.find_all("sup", class_="reference")
    for link in links:
        link.decompose()

    vehicle_list: List[Vehicle] = []

    # на одной странице может быть несколько инфобоксов
    infobox_list = soup.find_all("table", class_="infobox")

    # данные с первого инфобокса на странице содержат общую информацию
    first_infobox_data: Dict[str, str] = {}
    for idx, infobox in enumerate(infobox_list):
        if not isinstance(infobox, Tag):
            continue
        # Извлечение всех строк таблицы
        rows = infobox.find_all("tr")

        # Список для хранения данных таблицы
        table_data: List[List[str]] = []

        # Обработка каждой строки
        for row in rows:
            if not isinstance(row, Tag):
                continue
            # Извлечение ячеек (заголовков или данных)
            cells = [clean_cell(cell) for cell in row.find_all(["th", "td"]) if isinstance(cell, Tag)]
            table_data.append(cells)

        tmp_dict: Dict[str, str] = {}
        # заполнение словаря
        for i, row in enumerate(table_data):
            # первая строка - имя модели
            if i == 0:
                tmp_dict["model_name"] = create_model_name(title, row[0])

            if len(row) > 1:
                tmp_dict[str_to_column_name(row[0])] = row[1]
            else:
                tmp_dict[str_to_column_name(row[0])] = row[0]

        # объединение данных из первого инфобокса
        if idx == 0:
            first_infobox_data = tmp_dict
        else:
            tmp_dict = {**first_infobox_data, **tmp_dict}

        # обработка данных
        p_years = parse_years_range(tmp_dict.get("production"))
        engine = parse_engine(tmp_dict.get("engine"))
        electric_engine = parse_electric_engine(tmp_dict.get("electric_motor"))

        vehicle: Vehicle = {
            "url": url,
            "filepath": url_to_filepath(url),
            "model_name": tmp_dict.get("model_name", "unknown"),
            "model_code": tmp_dict.get("model_code"),
            "production_start_year": p_years[0],
            "production_end_year": p_years[1],
            "assembly_list": parse_assembly_countries(tmp_dict.get("assembly")),
            "manufacturer_list": parse_manufacturer_company(tmp_dict.get("manufacturer")),
            "engine_list": engine + electric_engine,
            "transmission_list": parse_transmission(tmp_dict.get("transmission")),
            "vehicle_class": parse_class(tmp_dict.get("class")),
            "body_style": parse_body_style(tmp_dict.get("body_style")),
            "layout": layout_parse(tmp_dict.get("layout")),
            "wheelbase": parse_meters(tmp_dict.get("wheelbase")),
            "length": parse_meters(tmp_dict.get("length")),
            "width": parse_meters(tmp_dict.get("width")),
            "height": parse_meters(tmp_dict.get("height")),
            "weight": parse_kilogrames(
                tmp_dict.get("weight") or tmp_dict.get("kerb_weight") or tmp_dict.get("curb_weight")
            ),
            "json": json.dumps(tmp_dict),
        }

        vehicle_list.append(vehicle)
    return vehicle_list
