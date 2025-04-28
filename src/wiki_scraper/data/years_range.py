import re
from datetime import datetime

re_remove_parentheses_comments = re.compile(r"\(.*?\)")  # Убираем скобки с комментариями
re_replace_present_current = re.compile(r"present|current")  # Заменяем 'present|current'
re_remove_spaces_around_dash = re.compile(r"\s?-\s?")  # Убираем лишние пробелы вокруг '-'
re_remove_words_between_years = re.compile(r"(?<=-)[^-\d]*(?:\d{1,2}[^\d;]*)?(?=\d{4})")  # удаляем слова между годами
re_fix_incomplete_range = re.compile(r"(?<=\d{4})-(?=;|$)")  # добавляем текущий год к диапазону

re_find_years_range = re.compile(r"\b(\d{4})(?:-)(\d{2}|\d{4})\b")  # Находим диапазон годов
re_find_single_year = re.compile(r"\b(\d{4})\b")  # Находим одиночный год


def parse_years_range(text: str | None) -> tuple[int | None, int | None]:
    """
    Извлекает минимальный и максимальный год производства из строки.
    """
    if text is None:
        return (None, None)

    current_year = datetime.now().year

    text = text.lower()
    text = text.replace(" to ", " - ")  # Заменяем 'to' на '-'
    text = re_remove_parentheses_comments.sub("", text)  # Убираем скобки с комментариями
    text = re_replace_present_current.sub(str(current_year), text)  # Заменяем 'present|current' на текущий год
    text = re_remove_spaces_around_dash.sub("-", text)  # Убираем лишние пробелы вокруг '-'
    text = re_remove_words_between_years.sub("", text)  # удаляем день и месяц из диапазона
    text = re_fix_incomplete_range.sub("-" + str(current_year), text)  # добавляем текущий год к диапазону

    # получение списка диапазонов годов
    ranges = re_find_years_range.findall(text)
    if ranges:
        years_list = []
        for range in ranges:
            start, end = range
            start = int(start)
            end = int(end)
            if end < 100:
                end += (start // 100) * 100
            years_list.append((start, end))
        min_year = min(years_list, key=lambda x: x[0])[0]
        max_year = max(years_list, key=lambda x: x[1])[1]
        return (min_year, max_year)

    # Получение одиночного года
    single_year_pattern = re_find_single_year.search(text)
    if single_year_pattern:
        year = int(single_year_pattern.group(1))
        # Очищаем от выбросов
        if year < 1885 or year > current_year:
            return (None, None)
        return (year, None)

    return (None, None)
