# training objects
from mlscraper.parser import Page


class MultiItemPageSample:
    """Sample of an item on a page containing several items."""

    page = None
    items = None

    def __init__(self, page: Page, items: list):
        self.page = page
        self.items = items


class SingleItemPageSample:
    """Sample of an item on a page containing one item only."""

    page = None
    item = None

    def __init__(self, page: Page, item: dict):
        self.page = page
        self.item = item
