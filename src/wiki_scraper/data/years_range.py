import re
from datetime import datetime

re_remove_parentheses_comments = re.compile(r"\(.*?\)")  # Убираем скобки с комментариями
re_replace_present_current = re.compile(r"present|current")  # Заменяем 'present|current'
re_remove_spaces_around_dash = re.compile(r"\s?-\s?")  # Убираем лишние пробелы вокруг '-'
re_remove_words_between_years = re.compile(r"(?<=-)[^-\d]*(?:\d{1,2}[^\d;]*)?(?=\d{4})")  # удаляем слова между годами
re_fix_incomplete_range = re.compile(r"(?<=\d{4})-(?=;|$)")  # добавляем текущий год к диапазону

re_find_years_range = re.compile(r"(\d{4})(?:-)(\d{2,4})")  # Находим диапазон годов
re_find_single_year = re.compile(r"\b(\d{4})\b")  # Находим одиночный год


def parse_years_range(text: str | None) -> tuple[int | None, int | None]:
    """
    Извлекает минимальный и максимальный год производства из строки.
    """
    if text is None:
        return (None, None)
    text = text.lower()
    text = text.replace(" to ", " - ")  # Заменяем 'to' на '-'
    text = re_remove_parentheses_comments.sub("", text)  # Убираем скобки с комментариями
    text = re_replace_present_current.sub(str(datetime.now().year), text)  # Заменяем 'present|current' на текущий год
    text = re_remove_spaces_around_dash.sub("-", text)  # Убираем лишние пробелы вокруг '-'
    text = re_remove_words_between_years.sub("", text)  # удаляем день и месяц из диапазона
    text = re_fix_incomplete_range.sub("-" + str(datetime.now().year), text)  # добавляем текущий год к диапазону

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

    single_year_pattern = re_find_single_year.search(text)
    if single_year_pattern:
        year = int(single_year_pattern.group(1))
        return (year, None)

    return (None, None)


if __name__ == "__main__":
    pass
    # print(parse_years_range("1941 - 1942, 1946 - 3 march 1948"), '\n')
