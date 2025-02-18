# Wiki Scraper

Этот проект предназначен для парсинга данных из Википедии с использованием Python и Poetry.

## Установка

1. **Клонируйте репозиторий:**

   ```sh
   git clone https://github.com/AntonS86/wiki-scraper
   cd wiki_scraper
   ```

2. **Установите Poetry (если не установлен):**

   ```sh
   pip install poetry
   ```

3. **Установите зависимости:**

   ```sh
   poetry install
   ```
4. **Создайте в корне папки html, db, logs**

## Использование

### Запуск скрипта

```sh
poetry run python src/wiki_scraper/main.py
```

### Запуск тестов

```sh
poetry run pytest
```

### Проверка кодстайла

```sh
poetry run black .
poetry run isort .
poetry run flake8
```

### Предкоммит хуки

Если предкоммит хуки не работают автоматически, их можно запустить вручную:

```sh
poetry run pre-commit run --all-files
```

## Структура проекта

```
wiki_scraper/
│   README.md           # Этот файл
│   pyproject.toml      # Конфигурация Poetry
│   poetry.lock         # Зафиксированные зависимости
├── html/               # Папка для сохранения HTML-кода
├── db/                 # Папка для сохранения базы данных
├── logs/               # Папка для сохранения логов
│
├── src/wiki_scraper/   # Основной код проекта
│   ├── crawler.py      # Логика парсинга
│   ├── scraper.py      # Основной обработчик данных
│   ├── storage.py      # Работа с файлами
│   ├── utils.py        # Вспомогательные функции
│   └── main.py         # Точка входа
│
├── tests/              # Тесты
└── .pre-commit-config.yaml # Настройки pre-commit
```

## Частые проблемы

### Poetry не находит зависимости

Попробуйте перегенерировать `poetry.lock` и переустановить зависимости:

```sh
poetry lock --no-update
poetry install
```

### Проблемы с предкоммит хуками

Если `pre-commit` форматирует файлы, но не даёт сделать коммит:

```sh
poetry run black .
poetry run isort .
poetry run flake8
poetry run pre-commit run --all-files
```

Затем добавьте изменения:

```sh
git add .
git commit -m "Исправлен формат кода"
```

## Контрибьюция

1. Форкните репозиторий
2. Создайте ветку с новой фичей (`git checkout -b feature-branch`)
3. Внесите изменения и закоммитьте (`git commit -m "Описание изменений"`)
4. Запустите тесты и форматирование
5. Откройте Pull Request

