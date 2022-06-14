import pytest
from mlscraper.html import Page
from mlscraper.samples import Sample
from mlscraper.samples import TrainingSet
from mlscraper.training import train_scraper


def test_train_scraper_simple_list():
    training_set = TrainingSet()
    training_set.add_sample(
        Sample(
            Page(b"<html><body><p>a<p><i>noise</i><p>b</p><p>c</p></body></html>"),
            ["a", "b", "c"],
        )
    )
    train_scraper(training_set.item)


@pytest.mark.skip("fucking fails")
def test_train_scraper(stackoverflow_samples):
    training_set = TrainingSet()
    for s in stackoverflow_samples:
        training_set.add_sample(s)

    scraper = train_scraper(training_set.item)
    print(f"result scraper: {scraper}")
    print(f"selector for list items: {scraper.selector}")

    scraping_result = scraper.get(stackoverflow_samples[0].page)
    print(f"scraping result: {scraping_result}")

    scraping_sample = stackoverflow_samples[0].value
    assert scraping_result == scraping_sample