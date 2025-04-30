from wiki_scraper.data.vehicle_class import parse_vehicle_class


def test_wiki_term_to_class():
    assert parse_vehicle_class("grand tourer") == "S"
    assert parse_vehicle_class("concept car") == "concept"
    assert parse_vehicle_class("Grand tourer ( S ) (coupe/convertible);Executive car ( E ) (Gran Coupe)") == "E;S"
    assert parse_vehicle_class("compact executive car") == "D"
    assert parse_vehicle_class("Mid-size/Full-size") == "D;E"
    assert parse_vehicle_class("Mid-size / Full-size") == "D;E"
    assert parse_vehicle_class("Subcompact executive car (2013-present) (C)") == "C"
