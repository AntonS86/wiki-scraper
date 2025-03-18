import sys

import pandas as pd
from SPARQLWrapper import JSON, SPARQLWrapper

from wiki_scraper.config import CSV_PATH


def get_results(endpoint_url, query):
    """
    Выполняет SPARQL-запрос к указанному endpoint.
    """
    user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)  # Указываем, что ожидаем ответ в формате JSON
    return sparql.query().convert()


def save_results_to_csv(results, output_filename):
    """
    Сохраняет результаты SPARQL-запроса в CSV-файл.
    """
    data = []

    for result in results["results"]["bindings"]:
        # Формируем словарь, где ключи - названия колонок, а значения - данные из запроса
        row = {col: result.get(col, {}).get("value", None) for col in results["head"]["vars"]}
        data.append(row)

    df = pd.DataFrame(data)  # Преобразуем список словарей в DataFrame
    df.to_csv(output_filename, index=False, encoding="utf-8")  # Сохраняем DataFrame в CSV-файл


endpoint_url = "https://query.wikidata.org/sparql"

query = """SELECT ?car ?carLabel ?brandLabel ?manufacturerLabel
  (YEAR(?inception) as ?inception_year) (YEAR(?startTime) as ?start_year) (YEAR(?endTime) as ?end_year)
  (YEAR(?productionDate) AS ?production_year) (YEAR(?discontinuedDate) AS ?discontinued_year)
  ?wheelbaseLabel ?lengthLabel ?heightLabel ?widthLabel ?massLabel
  ?subclassLabel
  ?engineLabel ?engineClassLabel ?engineSubclassLabel
  ?modelSeriesLabel (YEAR(?modelSeriesStartTime) as ?modelSeriesStartYear)
  (YEAR(?modelSeriesEndTime) as ?modelSeriesEndYear)
  ?wikipediaArticle
  WHERE {
  # Ищем элементы, которые являются экземплярами или подклассами "автомобиля" (Q3231690)
  ?car (wdt:P31/(wdt:P279*)) wd:Q3231690;
    # Указываем, что производитель — Toyota (Q53268)
    wdt:P176 wd:Q53268.

  # Опционально получаем бренд автомобиля
  OPTIONAL { ?car wdt:P1716 ?brand. }

  # Опционально получаем производителя автомобиля
  OPTIONAL { ?car wdt:P176 ?manufacturer. }

  # Опционально получаем дату создания автомобиля
  OPTIONAL { ?car wdt:P571 ?inception. }

  # Опционально получаем дату начала производства
  OPTIONAL { ?car wdt:P580 ?startTime. }

  # Опционально получаем дату окончания производства
  OPTIONAL { ?car wdt:P582 ?endTime. }

  # Опционально получаем дату производства
  OPTIONAL { ?car wdt:P2754 ?productionDate. }

  # Опционально получаем дату снятия с производства
  OPTIONAL { ?car wdt:P2669 ?discontinuedDate. }

  # Опционально получаем колёсную базу автомобиля
  OPTIONAL { ?car wdt:P3039 ?wheelbase. }

  # Опционально получаем длину автомобиля
  OPTIONAL { ?car wdt:P2043 ?length. }

  # Опционально получаем высоту автомобиля
  OPTIONAL { ?car wdt:P2048 ?height. }

  # Опционально получаем ширину автомобиля
  OPTIONAL { ?car wdt:P2049 ?width. }

  # Опционально получаем массу автомобиля
  OPTIONAL { ?car wdt:P2067 ?mass. }

  # Опционально получаем подкласс автомобиля
  OPTIONAL { ?car wdt:P279 ?subclass. }

  # Опционально получаем информацию о двигателе
  OPTIONAL {
    ?car wdt:P516 ?engine.
    ?engine wdt:P279 ?engineClass.
    ?engine wdt:P31 ?engineSubclass.
  }

  # Опционально получаем информацию о серии моделей
  OPTIONAL {
    ?car wdt:P179 ?modelSeries.
    ?modelSeries wdt:P580 ?modelSeriesStartTime.
    ?modelSeries wdt:P582 ?modelSeriesEndTime.
  }

  # Опционально получаем ссылку на статью в Wikipedia
  OPTIONAL {
    ?wikipediaArticle schema:about ?car.
    ?wikipediaArticle schema:isPartOf <https://en.wikipedia.org/>.
  }

  # Добавляем метки на английском языке
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
# Ограничиваем количество результатов 100 записями
LIMIT 5"""

if __name__ == "__main__":
    results = get_results(endpoint_url, query)  # Получаем данные из Wikidata
    save_results_to_csv(results, CSV_PATH / "wikidata_cars.csv")  # Сохраняем в CSV-файл
