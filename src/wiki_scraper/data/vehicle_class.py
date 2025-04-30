import re

wiki_term_to_class = {
    # Класс A — миникары
    "microcar": "A",
    "city car": "A",
    "kei car": "A",  # японский подтип microcar
    "urban car": "A",
    "quadricycle": "A",
    "small car": "A",
    # Класс B — субкомпакты
    "economy car": "B",
    "supermini": "B",
    "light car": "B",  # термин в Австралии
    "compact city car": "B",
    "subcompact": "B",
    "b-segment": "B",
    # Класс C — компакты
    "small family car": "C",
    "family car": "C",
    "compact car": "C",
    "compact": "C",
    "hatchback": "C",
    "sedan (compact)": "C",
    "subcompact executive car": "C",
    "taxicab": "C",  # такси
    # Класс D — средний класс
    "large family car": "D",
    "mid-size car": "D",
    "mid-size": "D",
    "midsize": "D",
    "medium": "D",
    "compact executive car": "D",
    # Класс E — бизнес-класс
    "executive car": "E",
    "full-size car": "E",
    "full-size": "E",
    "full size": "E",
    "large sedan": "E",
    # Класс F — представительский
    "luxury car": "F",
    "luxury": "F",
    "full-size luxury car": "F",
    "luxury sedan": "F",
    "limousine": "F",
    # Класс S — спортивные
    "sport car": "S",
    "sports car": "S",
    "sport compact": "S",
    "grand tourer": "S",
    "roadster": "S",
    "coupe": "S",
    "convertible": "S",
    "supercar": "S",
    "muscle car": "S",
    "track car": "S",
    "pony car": "S",
    "hot hatch": "S",
    # Класс M — минивэны и MPV
    "mpv": "M",  # multi-purpose vehicle
    "minivan": "M",
    "compact mpv": "M",
    "large mpv": "M",
    "people carrier": "M",
    "light commercial vehicle": "M",
    "light truck": "M",
    "key truck": "M",
    "truck": "M",
    # Класс J — SUV и внедорожники
    "suv": "J",
    "crossover": "J",
    "off-road vehicle": "J",
    "4x4": "J",
    "jeep": "J",
    "cuv": "J",  # crossover utility vehicle
    # Дополнительно (по контексту могут быть отнесены)
    "pickup truck": "J",  # иногда относят к J
    "ute": "J",  # термин в Австралии
    "van": "M",  # зависит от размера
    "panel van": "M",  # коммерческий фургон
    "station wagon": "C",  # обычно производные от C или D
    "estate car": "C",  # аналогично
    # Не входящие в классификацию
    "concept car": "concept",
    "grand prix": "racing",
    "racing car": "racing",
    "race car": "racing",
    "wsc racer": "racing",
}

re_replace_delimiters = re.compile(r"(?<=[a-z])\s?/\s?(?=[a-z])")  # Заменяем разделители "/" на ";"

# Предварительная сортировка ключей (оптимизируется один раз)
sorted_keys = sorted(wiki_term_to_class.keys(), key=len, reverse=True)


def parse_vehicle_class(text: str | None) -> str | None:
    if text is None:
        return None
    text = text.lower()
    text = re_replace_delimiters.sub(";", text)  # Заменяем разделители "/" на ";"
    find_set: set[str] = set()
    for part in text.split(";"):
        for key in sorted_keys:
            if key in part:
                find_set.add(wiki_term_to_class[key])
                break

    return ";".join(sorted(find_set)) if find_set else None
