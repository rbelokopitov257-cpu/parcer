"""Scrapers package — each source in its own module."""

from abc import ABC, abstractmethod
from database import Startup


class BaseScraper(ABC):
    """Interface that every scraper must implement."""

    name: str = "base"

    @abstractmethod
    def scrape(self) -> list[Startup]:
        """Fetch and return a list of Startup objects."""
        ...


# Import all scrapers so they can be discovered
from scrapers.hackernews import HackerNewsScraper
from scrapers.producthunt import ProductHuntScraper
from scrapers.techcrunch import TechCrunchScraper
from scrapers.reddit import RedditScraper

ALL_SCRAPERS: list[type[BaseScraper]] = [
    HackerNewsScraper,
    ProductHuntScraper,
    TechCrunchScraper,
    RedditScraper,
]
