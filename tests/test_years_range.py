from datetime import datetime

from wiki_scraper.data.years_range import parse_years_range


def test_parse_years_range():
    current_year = datetime.now().year
    assert parse_years_range("2000 - 2005") == (2000, 2005)
    assert parse_years_range("2000 - present") == (2000, current_year)
    assert parse_years_range("2000 - current") == (2000, current_year)
    assert parse_years_range("1975 - 3 December 1979") == (1975, 1979)
    assert parse_years_range("1958") == (1958, None)
    assert parse_years_range("2009-") == (2009, current_year)
    assert parse_years_range("2025 (to commence, 10 units planned)") == (2025, None)
    assert parse_years_range("1938-40: 7,470 units") == (1938, 1940)
    assert parse_years_range("1969 - end of 1973") == (1969, 1973)
    assert parse_years_range("1937 to 1940") == (1937, 1940)
    assert parse_years_range("January 1989-August 25, 1994") == (1989, 1994)
    assert parse_years_range("March 7, 1994 - April 26, 2001") == (1994, 2001)

    assert parse_years_range("1941 - 1942, 1946 - 3 march 1948") == (1941, 1948)
    assert parse_years_range("1969-2006 (Romania);1975-1995 (Portugal);1980-1990 (Spain);2002-2006 (Brazil)") == (
        1969,
        2006,
    )
    assert parse_years_range("1920-27;1500 approx produced") == (1920, 1927)
    assert parse_years_range("4050") == (None, None)
    assert parse_years_range("1978-200?") == (1978, None)
