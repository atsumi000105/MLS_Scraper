"""
Matches are specific elements found on a page that match a sample.
"""
import logging
import typing

from mlscraper.html import AttributeMatch
from mlscraper.html import get_root_node
from mlscraper.html import Node
from mlscraper.html import TextMatch
from mlscraper.selectors import Selector


class Match:
    """
    Occurrence of a specific sample on a page
    """

    @property
    def root(self) -> Node:
        """
        The lowest element that contains matched elements.
        """
        raise NotImplementedError()


class Extractor:
    """
    Class that extracts values from a node.
    """

    def extract(self, node: Node):
        raise NotImplementedError()


class Matcher:
    """
    Class that finds/selects nodes and extracts items from these nodes.
    """

    selector = None
    extractor = None

    def __init__(self, selector: Selector, extractor: Extractor):
        self.selector = selector
        self.extractor = extractor

    def match_one(self, node: Node) -> Match:
        selected_node = self.selector.select_one(node)
        return Match(selected_node, self.extractor)

    def match_all(self, node: Node) -> typing.List[Match]:
        selected_nodes = self.selector.select_all(node)
        return [Match(n, self.extractor) for n in selected_nodes]

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.selector=} {self.extractor=}>"


class TextValueExtractor(Extractor):
    """
    Class to extract text from a node.
    """

    def extract(self, node: Node):
        return node.soup.text

    def __repr__(self):
        return f"<{self.__class__.__name__}>"

    def __hash__(self):
        # todo each instance equals each other instance,
        #  so this holds,
        #  but it isn't pretty
        return 0

    def __eq__(self, other):
        return isinstance(other, TextValueExtractor)


class AttributeValueExtractor(Extractor):
    """
    Extracts a value from the attribute in an html tag.
    """

    attr = None

    def __init__(self, attr):
        self.attr = attr

    def extract(self, node: Node):
        if self.attr in node.soup.attrs:
            return node.soup[self.attr]

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.attr=}>"

    def __hash__(self):
        return self.attr.__hash__()

    def __eq__(self, other):
        return isinstance(other, AttributeValueExtractor) and self.attr == other.attr


class DictExtractor(Extractor):
    def __init__(self, matcher_by_key: typing.Dict[str, Matcher]):
        self.matcher_by_key = matcher_by_key

    def extract(self, node: Node):
        return {
            key: matcher.match_one(node) for key, matcher in self.matcher_by_key.items()
        }


class DictMatch(Match):
    match_by_key = None

    def __init__(self, match_by_key: dict):
        self.match_by_key = match_by_key

    @property
    def root(self) -> Node:
        match_roots = [m.root for m in self.match_by_key.values()]
        return get_root_node(match_roots)

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.match_by_key=}>"


class ListMatch(Match):
    matches = None

    def __init__(self, matches: tuple):
        self.matches = matches

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.matches=}>"

    @property
    def root(self) -> Node:
        return get_root_node([m.root for m in self.matches])


class ValueMatch(Match):
    node = None
    extractor = None

    def __init__(self, node: Node, extractor: Extractor):
        self.node = node
        self.extractor = extractor

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.node=}, {self.extractor=}>"

    @property
    def root(self) -> Node:
        return self.node


def generate_all_value_matches(
    node: Node, item: str
) -> typing.Generator[Match, None, None]:
    logging.info(f"generating all value matches ({node=}, {item=})")
    for html_match in node.find_all(item):
        matched_node = html_match.node
        if isinstance(html_match, TextMatch):
            extractor = TextValueExtractor()
        elif isinstance(html_match, AttributeMatch):
            extractor = AttributeValueExtractor(html_match.attr)
        else:
            raise RuntimeError(
                f"unknown match type ({html_match=}, {type(html_match)=})"
            )
        yield ValueMatch(matched_node, extractor)
