from bs4 import BeautifulSoup
from mlscraper.util import _get_root_of_nodes
from mlscraper.util import AttributeValueExtractor
from mlscraper.util import get_attribute_extractor
from mlscraper.util import Node
from mlscraper.util import Page


class TestPage:
    def test_something(self, stackoverflow_samples):
        page = stackoverflow_samples[0].page
        nodes = page.select(".answer .js-vote-count")
        assert [n.text for n in nodes] == ["20", "16", "0"]

    def test_find_all(self, stackoverflow_samples):
        page = stackoverflow_samples[0].page
        nodes = page.find_all("/users/624900/jterrace")
        assert nodes


def test_attribute_extractor():
    soup = BeautifulSoup(
        '<html><body><a href="http://karllorey.com"></a><a>no link</a></body></html>',
        "lxml",
    )
    ue = AttributeValueExtractor("href")
    a_tags = soup.find_all("a")
    assert ue.extract(Node(a_tags[0])) == "http://karllorey.com"
    assert ue.extract(Node(a_tags[1])) is None


def test_extractor_factory():
    # we want to make sure that each extractor exists only once
    # as we need this to ensure extractor selection
    e1 = get_attribute_extractor("href")
    e2 = get_attribute_extractor("href")
    assert (
        e1 is e2
    ), "extractor factory returns different instances for the same extractor"


def test_get_root_of_nodes():
    soup = BeautifulSoup(
        '<html><body><div><p id="one"></p><p><span id="two"></span></p></div></body></html>',
        "lxml",
    )
    node_1 = soup.select_one("#one")
    node_2 = soup.select_one("#two")
    root = _get_root_of_nodes([node_1, node_2])
    assert root == soup.select_one("div")
