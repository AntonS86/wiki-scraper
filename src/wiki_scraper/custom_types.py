from typing import List, Optional, TypedDict


class Engine(TypedDict):
    text: str
    type_fuel: Optional[str]
    volume: Optional[float]
    power: Optional[float]


class Transmission(TypedDict):
    text: str
    type: Optional[str]
    speed: Optional[int]


class Vehicle(TypedDict):
    url: str
    filepath: str
    model_name: str
    model_code: Optional[str]
    # год начала и конца производства
    production_start_year: Optional[int]
    production_end_year: Optional[int]
    # страна сборки
    assembly_list: List[str]
    # производитель
    manufacturer_list: List[str]
    # двигатель + электродвигатель
    engine_list: List[Engine]
    # коробка передач
    transmission_list: List[Transmission]
    # класс
    vehicle_class: Optional[str]
    # тип кузова
    body_style: Optional[str]
    # расположение двигателя
    layout: Optional[str]
    # длина колесной базы
    wheelbase: Optional[float]
    # длина
    length: Optional[float]
    # ширина
    width: Optional[float]
    # высота
    height: Optional[float]
    # вес
    weight: Optional[float]
    # json строка данных из infobox
    json: str
