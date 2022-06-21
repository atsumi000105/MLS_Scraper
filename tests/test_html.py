from bs4 import BeautifulSoup
from mlscraper.html import _get_root_of_nodes
from mlscraper.html import HTMLTextMatch
from mlscraper.html import Page
from mlscraper.html import selector_matches_nodes
from mlscraper.matches import AttributeValueExtractor


def test_get_root_of_nodes():
    soup = BeautifulSoup(
        b'<html><body><div><p id="one"></p><p><span id="two"></span></p></div></body></html>',
        "lxml",
    )
    node_1 = soup.select_one("#one")
    node_2 = soup.select_one("#two")
    root = _get_root_of_nodes([node_1, node_2])
    assert root == soup.select_one("div")


class TestPage:
    def test_select(self, stackoverflow_samples):
        page = stackoverflow_samples[0].page
        nodes = page.select(".answer .js-vote-count")
        assert [n.text for n in nodes] == ["20", "16", "0"]

    def test_find_all(self, stackoverflow_samples):
        page = stackoverflow_samples[0].page
        nodes = page.find_all("/users/624900/jterrace")
        assert nodes


def test_attribute_extractor():
    html_ = (
        b'<html><body><a href="https://karllorey.com"></a><a>no link</a></body></html>'
    )
    page = Page(html_)
    extractor = AttributeValueExtractor("href")
    a_tags = page.select("a")
    assert extractor.extract(a_tags[0]) == "https://karllorey.com"
    assert extractor.extract(a_tags[1]) is None


def test_extractor_factory():
    # we want to make sure that each extractor exists only once
    # as we need this to ensure extractor selection
    e1 = AttributeValueExtractor("href")
    e2 = AttributeValueExtractor("href")
    assert len({e1, e2}) == 1


def test_equality():
    # we want to make sure that equal html does not result in equality
    same_html = b"<html><body><div><p></p></div></body></html>"
    assert Page(same_html) == Page(same_html)
    assert Page(same_html) is not Page(same_html)


def test_select():
    html = b"<html><body><p></p><p></p></body></html>"
    page = Page(html)
    p_tag_nodes = page.select("p")
    assert len(p_tag_nodes) == 2
    # not used in practice
    # assert len(set(p_tag_nodes)) == 2


def test_tag_name():
    html = b"<html><body><p>bla</p></body></html>"
    p = Page(html)
    tag_node = p.select("p")[0]
    assert tag_node.tag_name == "p"


def test_classes():
    html = b'<html><body><p class="box bordered">bla</p></body></html>'
    p = Page(html)
    tag_node = p.select("p")[0]
    assert tag_node.classes == ["box", "bordered"]


def test_selector_matches_nodes():
    html = b"<html><body><p>1</p><p>2</p></body></html>"
    page = Page(html)

    p_tags = page.select("p")
    assert selector_matches_nodes(
        page, "p", p_tags
    ), "does not match properly ordered tags"

    p_tags_reversed = list(reversed(p_tags))
    assert not selector_matches_nodes(
        page, "p", p_tags_reversed
    ), "matches reversed order"


def test_find_text_with_whitespace():
    html = b"<html><body><p>    whitespace  \n\t </p></body></html>"
    page = Page(html)
    html_matches = page.find_all("whitespace")
    assert len(html_matches) == 1
    assert isinstance(html_matches[0], HTMLTextMatch)
