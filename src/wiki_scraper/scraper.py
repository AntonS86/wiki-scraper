from bs4 import BeautifulSoup

from wiki_scraper.utils import (
    classify_page,
    clean_html,
    clean_wiki_url,
    get_wiki_links,
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
