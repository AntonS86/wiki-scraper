import re

re_replace_num_commas = re.compile(r"(?<=\d),(?=\d)")

re_replace_millimeters = re.compile(r"\bmillimeters\b|\bmillimetres\b")
re_find_mm = re.compile(r"\b(\d+(?:\.\d+)?) ?mm\b")

re_replace_meters = re.compile(r"\bmeters\b|\bmetres\b")
re_find_m = re.compile(r"\b(\d+(?:\.\d+)?) ?m\b")

re_replace_centimeters = re.compile(r"\bcentimeters\b|\bcentimetres\b")
re_find_cm = re.compile(r"\b(\d+(?:\.\d+)?) ?cm\b")

re_replace_inches = re.compile(r"\binches\b")  # Заменяем 'inches' на 'in'
re_find_in = re.compile(r"\b(\d+(?:\.\d+)?) ?in\b")


def find_max_meters(text: str | None) -> float | None:
    """
    Находит в строке максимальное значение в метрах,
    конвертируя другие единицы измерения
    """
    if text is None:
        return None

    # убираем запятые
    text = text.lower()
    text = re_replace_num_commas.sub("", text)
    # поиск в миллиметрах
    text = re_replace_millimeters.sub("mm", text)  # Заменяем 'millimeters' на 'mm'
    dimensions_mm = re_find_mm.findall(text)
    if dimensions_mm:
        dimensions_mm = list(map(lambda x: float(x), dimensions_mm))
        max_mm = max(dimensions_mm)
        return max_mm / 1000

    # поиск в метрах
    text = re_replace_meters.sub("m", text)  # Заменяем 'meters' на 'm'
    dimensions_m = re_find_m.findall(text)
    if dimensions_m:
        dimensions_m = list(map(lambda x: float(x), dimensions_m))
        max_m = max(dimensions_m)
        return max_m

    # поиск в сантиметрах
    text = re_replace_centimeters.sub("cm", text)  # Заменяем 'centimeters' на 'cm'
    dimensions_cm = re_find_cm.findall(text)
    if dimensions_cm:
        dimensions_cm = list(map(lambda x: float(x), dimensions_cm))
        max_cm = max(dimensions_cm)
        return max_cm / 100

    # поиск в дюймах
    text = re_replace_inches.sub("in", text)  # Заменяем 'inches' на 'in'
    dimensions_in = re_find_in.findall(text)
    if dimensions_in:
        dimensions_in = list(map(lambda x: float(x), dimensions_in))
        max_in = max(dimensions_in)
        return round(max_in * 0.0254, 4)
    return None


re_replace_kilograms = re.compile(r"\bkilograms\b")  # Заменяем 'kilograms' на 'kg'
re_find_kg = re.compile(r"\b(\d+(?:\.\d+)?) ?kg\b")

re_replace_pounds = re.compile(r"\bpounds\b|(?<=\s|\d)lbs\b")  # Заменяем 'pounds' на 'lb'
re_find_lb = re.compile(r"\b(\d+(?:\.\d+)?) ?lb\b")

re_replace_tons = re.compile(r"\btons\b|\btonnes\b")  # Заменяем 'tons' на 't'
re_find_t = re.compile(r"\b(\d+(?:\.\d+)?) ?t\b")

re_find_cwt = re.compile(r"\b(\d+(?:\.\d+)?) ?cwt\b")


def find_max_kilograms(text: str | None) -> float | None:
    """
    Находит в строке максимальное значение в килограммах,
    конвертируя другие единицы измерения
    """
    if text is None:
        return None
    # убираем запятые
    text = text.lower()
    text = re_replace_num_commas.sub("", text)
    # поиск в килограммах
    text = re_replace_kilograms.sub("kg", text)  # Заменяем 'kilograms' на 'kg'
    dimensions_kg = re_find_kg.findall(text)
    if dimensions_kg:
        dimensions_kg = list(map(lambda x: float(x), dimensions_kg))
        max_kg = max(dimensions_kg)
        return max_kg

    # поиск в тоннах
    text = re_replace_tons.sub("t", text)  # Заменяем 'tons' на 't'
    dimensions_t = re_find_t.findall(text)
    if dimensions_t:
        dimensions_t = list(map(lambda x: float(x), dimensions_t))
        max_t = max(dimensions_t)
        return round(max_t * 1000, 4)

    # поиск в фунтах
    text = re_replace_pounds.sub("lb", text)  # Заменяем 'pounds' на 'lb'
    dimensions_lb = re_find_lb.findall(text)
    if dimensions_lb:
        dimensions_lb = list(map(lambda x: float(x), dimensions_lb))
        max_lb = max(dimensions_lb)
        return round(max_lb * 0.4536, 4)

    # поиск в cwt
    dimensions_cwt = re_find_cwt.findall(text)
    if dimensions_cwt:
        dimensions_cwt = list(map(lambda x: float(x), dimensions_cwt))
        max_cwt = max(dimensions_cwt)
        return round(max_cwt * 50.8023, 4)

    return None
