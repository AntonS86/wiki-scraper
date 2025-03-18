import re

from wiki_scraper.custom_types import ListClassifyPattern

layout_patterns: ListClassifyPattern = [
    {"words": ["front-engine", "fwd"], "category": "front-engine, front-wheel-drive"},
    {"words": ["front-engine", "rwd"], "category": "front-engine, rear-wheel-drive"},
    {"words": ["front-engine", "4wd"], "category": "front-engine, four-wheel-drive"},
    {"words": ["front-engine", "awd"], "category": "front-engine, all-wheel-drive"},
    {"words": ["mid-engine", "fwd"], "category": "mid-engine, front-wheel-drive"},
    {"words": ["mid-engine", "rwd"], "category": "mid-engine, rear-wheel-drive"},
    {"words": ["mid-engine", "4wd"], "category": "mid-engine, four-wheel-drive"},
    {"words": ["mid-engine", "awd"], "category": "mid-engine, all-wheel-drive"},
    {"words": ["rear-engine", "fwd"], "category": "rear-engine, front-wheel-drive"},
    {"words": ["rear-engine", "rwd"], "category": "rear-engine, rear-wheel-drive"},
    {"words": ["rear-engine", "4wd"], "category": "rear-engine, four-wheel-drive"},
    {"words": ["rear-engine", "awd"], "category": "rear-engine, all-wheel-drive"},
    {"words": ["dual-engine", "4wd"], "category": "dual-engine, four-wheel-drive"},
    {"words": ["dual-engine", "awd"], "category": "dual-engine, all-wheel-drive"},
]

layout_single_patterns: list[tuple[str, str]] = [
    ("fwd", "front-wheel-drive"),
    ("rwd", "rear-wheel-drive"),
    ("4wd", "four-wheel-drive"),
    ("awd", "all-wheel-drive"),
]

replacements: list[tuple[re.Pattern, str]] = [
    # ----------
    (re.compile(r"\bfront engine\b"), "front-engine"),
    (re.compile(r"\bmid engine\b"), "mid-engine"),
    (re.compile(r"\brear engine\b"), "rear-engine"),
    (re.compile(r"\bdual engine\b"), "dual-engine"),
    (re.compile(r"\bfront motor\b"), "front-engine"),
    (re.compile(r"\bmid motor\b"), "mid-engine"),
    (re.compile(r"\brear motor\b"), "rear-engine"),
    (re.compile(r"\bdual motor\b"), "dual-engine"),
    (re.compile(r"\bfront wheel drive\b"), "fwd"),
    (re.compile(r"\brear wheel drive\b"), "rwd"),
    (re.compile(r"\bfour wheel drive\b"), "4wd"),
    (re.compile(r"\ball wheel drive\b"), "awd"),
    # ---------
    (re.compile(r"\bff\b"), "front-engine fwd"),
    (re.compile(r"\bfr\b"), "front-engine rwd"),
    (re.compile(r"\bf4\b"), "front-engine 4wd"),
    (re.compile(r"\bmf\b"), "mid-engine fwd"),
    (re.compile(r"\bmr\b"), "mid-engine rwd"),
    (re.compile(r"\bm4\b"), "mid-engine 4wd"),
    (re.compile(r"\brf\b"), "rear-engine fwd"),
    (re.compile(r"\brr\b"), "rear-engine rwd"),
    (re.compile(r"\br4\b"), "rear-engine 4wd"),
]


def normalize_text(text: str, replacements: list[tuple[re.Pattern, str]]) -> str:
    text = text.lower()  # Приводим к нижнему регистру
    text = re.sub(r"[^\w]", " ", text)  # Убираем не словесные символы
    text = re.sub(r"\s{2,}", " ", text)  # убираем двойные пробелы

    for pattern, replacement in replacements:
        text = pattern.sub(replacement, text)  # Заменяем по словарю
    return text


def classify_layout(
    text: str,
) -> set[str]:
    """
    Классификация layout/компоновки автомобиля
    """
    text = normalize_text(text, replacements)
    cats: set[str] = set()
    # поиск категорий состоящий из комбинаций слов
    for pt in layout_patterns:
        if all(word in text for word in pt["words"]):
            cats.add(pt["category"])
    if cats:
        return cats
    # поиск категорий состоящих из единственных слов
    for pattern, category in layout_single_patterns:
        if pattern in text:
            cats.add(category)
    if cats:
        return cats
    # если ничего не нашли
    cats.add("unknown")
    return cats
