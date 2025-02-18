from bs4 import BeautifulSoup

from wiki_scraper.utils import (
    classify_page,
    clean_html,
    clean_wiki_url,
    create_model_name,
    get_wiki_links,
    str_to_column_name,
    url_to_filepath,
)


# парсинг страницы википедии и классификация по категориям
def parse_wikipedia_page(url, response_text):
    # путь к файлу
    filepath = url_to_filepath(url)

    soup = BeautifulSoup(response_text, "html.parser")

    # получаем ссылки на страницы внутри википедии
    links = get_wiki_links(soup)

    # очищаем страницу от скриптов, картинок, стилей и т.д.
    soup = clean_html(soup)

    # поиск заголовка страницы
    title = ""
    page_title = soup.find("h1", class_="mw-first-heading")
    if page_title:
        title = page_title.get_text()

    # классификация по содержимому
    category = classify_page(clean_wiki_url(url), soup)

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
def clean_text(text, default="N/A"):
    """
    Очищает текст: удаляет лишние пробелы, заменяет \xa0 на пробелы
    и возвращает значение по умолчанию, если текст пустой.
    """
    if text is None:
        return default
    cleaned_text = text.strip().replace("\xa0", " ")
    return cleaned_text if cleaned_text else default


def clean_cell(cell):
    """обработка и извлечение текста из ячейки"""

    # обработка td
    # поиск списков
    lis = cell.find_all("li")
    if len(lis) > 0:
        lst = [clean_text(li.text) for li in lis]
        return "; ".join(lst)

    # поиск списков с разделителями <br>
    brs = cell.find_all("br")
    if len(brs) > 0:
        # замена <br> на строковый разделитель
        for br in brs:
            br.replace_with("\n")
        lst = [clean_text(li) for li in cell.get_text(strip=True).split("\n")]
        return "; ".join(lst)

    # в остальных случаях
    # TODO: доработать обработку
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

    # словарь с данными по умолчанию
    default_dict = {
        "url": url,
        "filepath": url_to_filepath(url),
        "model_name": None,
        "also_called": None,
        "model_code": None,
        "production": None,
        "model_years": None,
        "assembly": None,
        "manufacturer": None,
        "class": None,
        "body_style": None,
        "platform": None,
        "engine": None,
        "electric_motor": None,
        "electric_range": None,
        "power_output": None,
        "transmission": None,
        "battery": None,
        "wheelbase": None,
        "layout": None,
        "length": None,
        "width": None,
        "height": None,
        "weight": None,
        "kerb_weight": None,
        "curb_weight": None,
    }

    data_dict_list = []

    # на одной странице может быть несколько инфобоксов
    infobox_list = soup.find_all("table", class_="infobox")

    for infobox in infobox_list:
        # Извлечение всех строк таблицы
        rows = infobox.find_all("tr")

        # Список для хранения данных таблицы
        table_data = []

        # Обработка каждой строки
        for row in rows:
            # Извлечение ячеек (заголовков или данных)
            cells = [clean_cell(cell) for cell in row.find_all(["th", "td"])]
            table_data.append(cells)

        tmp_dict = {}
        # заполнение словаря
        for i, row in enumerate(table_data):
            # первая строка - имя модели
            if i == 0:
                tmp_dict["model_name"] = create_model_name(title, row[0])

            if len(row) > 1:
                tmp_dict[str_to_column_name(row[0])] = row[1]
            else:
                tmp_dict[str_to_column_name(row[0])] = row[0]

        # объединение словарей
        data_dict = {**default_dict, **tmp_dict}
        data_dict_list.append(data_dict)
    return data_dict_list
