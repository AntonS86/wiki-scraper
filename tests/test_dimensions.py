from wiki_scraper.data.dimensions import find_max_kilograms, find_max_meters


def test_find_max_millimeters():
    assert find_max_meters("2896mm") == 2.896
    assert find_max_meters("3124 mm (123 in);3226 mm (127 in)") == 3.226
    assert find_max_meters("2,622 mm (103.2 in)") == 2.622
    assert find_max_meters("116.4 in (2,957 mm) (STS SWB);120.3 in (3,056 mm) (SLS LWB)") == 3.056
    assert find_max_meters("3,090 millimetres (121.7 in)") == 3.090
    assert find_max_meters("3,090 millimeters (121.7 in)") == 3.090


def test_find_max_centimeters():
    assert find_max_meters("310 cm (122.0 in);337 cm (132.7 in)(long version)") == 3.37
    assert find_max_meters("1,800 centimeters (71 in)") == 18
    assert find_max_meters("1,800 centimetres (71 in)") == 18
    assert find_max_meters("1800 cm (71 in)") == 18


def test_find_max_meters():
    assert find_max_meters("1.88 m (74.2 in)") == 1.88
    assert find_max_meters("1.65 metres (65 in)") == 1.65
    assert find_max_meters("1.65 meters (65 in)") == 1.65


def test_find_max_inches():
    assert find_max_meters("100 in") == 2.54
    assert find_max_meters("50 inches") == 1.27


def test_find_max_meters_none():
    assert find_max_meters(None) is None
    assert find_max_meters("") is None
    assert find_max_meters(" ") is None
    assert find_max_meters("some text") is None


def test_find_max_kilograms():
    assert find_max_kilograms("2896 kg") == 2896
    assert find_max_kilograms("3124kg (123 lb);3226kg (127 lb)") == 3226
    assert find_max_kilograms("3,090 kilograms (121.7 lb)") == 3090


def test_find_max_tons():
    assert find_max_kilograms("3.090 tons (121.7 lb)") == 3090
    assert find_max_kilograms("3.090 tonnes (121.7 lb)") == 3090
    assert find_max_kilograms("3.090 t (121.7 lb)") == 3090
    assert find_max_kilograms("36 tons (33t) (empty);86 tons (78t) (loaded)") == 86000


def test_find_max_pounds():
    assert find_max_kilograms("100 lb") == 45.36
    assert find_max_kilograms("50 pounds") == 22.68
    assert find_max_kilograms("3,090 pounds") == 1401.624
    assert find_max_kilograms("3,090 lbs") == 1401.624
    assert find_max_kilograms("1700lbs.") == 771.12


def test_find_max_cwt():
    assert find_max_kilograms("100 cwt") == 5080.23
    assert find_max_kilograms("50 cwt") == 2540.115
    assert find_max_kilograms("3,090 cwt") == 156979.107


def test_find_max_kilograms_none():
    assert find_max_kilograms(None) is None
    assert find_max_kilograms("") is None
    assert find_max_kilograms(" ") is None
    assert find_max_kilograms("some text") is None
