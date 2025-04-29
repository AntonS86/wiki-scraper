import pytest
from bs4 import BeautifulSoup, Tag

from wiki_scraper.scraper import clean_cell


def test_clean_cell_br_and_ul():
    html = """<td class="infobox-data">1962-1968<br>11,346 produced:<ul><li>2,092 Berlina</li>
            <li>6,999 Sprint</li>
            <li>105 Sprint Zagato</li>
           </ul></td>"""
    soup = BeautifulSoup(html, "html.parser")
    td = soup.find("td")
    if not isinstance(td, Tag):
        pytest.fail("td is not instance Tag")
    assert clean_cell(td) == "1962-1968;11,346 produced:;2,092 Berlina;6,999 Sprint;105 Sprint Zagato"


def test_clean_cell_after_unwrap_tags():
    html = (
        '<td><i>2,928</i>&nbsp;<a href="/wiki/Millimetre">mm</a> (<i>115.3</i>&nbsp;<a href="/wiki/Inch">in</a>)</td>'
    )
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all(["a", "i", "b"]):
        if isinstance(tag, Tag):
            tag.unwrap()
    td = soup.find("td")
    if not isinstance(td, Tag):
        pytest.fail("td is not instance Tag")
    assert clean_cell(td) == "2,928 mm (115.3 in)"
