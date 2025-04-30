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


def test_clean_cell_after_unwrap_tags2():
    html = '<td class="infobox-data"><a href="/wiki/Grand_tourer" title="Grand tourer">Grand tourer</a>, <a href="/wiki/Muscle_car" title="Muscle car">Muscle car</a>, <a href="/wiki/Sports_car" title="Sports car">Sports car</a><sup id="cite_ref-Discovery_2-0" class="reference"><a href="#cite_note-Discovery-2"><span class="cite-bracket">[</span>2<span class="cite-bracket">]</span></a></sup><sup id="cite_ref-art_3-0" class="reference"><a href="#cite_note-art-3"><span class="cite-bracket">[</span>3<span class="cite-bracket">]</span></a></sup><sup id="cite_ref-4" class="reference"><a href="#cite_note-4"><span class="cite-bracket">[</span>4<span class="cite-bracket">]</span></a></sup><sup id="cite_ref-5" class="reference"><a href="#cite_note-5"><span class="cite-bracket">[</span>5<span class="cite-bracket">]</span></a></sup></td>'  # noqa E501
    soup = BeautifulSoup(html, "html.parser")
    links = soup.find_all("sup", class_="reference")
    for link in links:
        link.decompose()
    for tag in soup.find_all(["a", "i", "b"]):
        if isinstance(tag, Tag):
            tag.unwrap()
    td = soup.find("td")
    if not isinstance(td, Tag):
        pytest.fail("td is not instance Tag")
    assert clean_cell(td) == "Grand tourer, Muscle car, Sports car"


def test_clean_cell_after_unwrap_tags3():
    html = """<td class="infobox-data"><a href="/wiki/Personal_luxury_car" title="Personal luxury car">Personal luxury car</a><br>
<a href="/wiki/Executive_car" title="Executive car">Executive car</a> (<a href="/wiki/E-segment" title="E-segment">E</a>)</td>"""  # noqa E501
    soup = BeautifulSoup(html, "html.parser")
    links = soup.find_all("sup", class_="reference")
    for link in links:
        link.decompose()
    for tag in soup.find_all(["a", "i", "b"]):
        if isinstance(tag, Tag):
            tag.unwrap()
    td = soup.find("td")
    if not isinstance(td, Tag):
        pytest.fail("td is not instance Tag")
    assert clean_cell(td) == "Personal luxury car;Executive car (E)"
