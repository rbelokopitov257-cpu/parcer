"""TechCrunch — RSS feeds for startups & funding sections."""

import logging
import feedparser
from scrapers import BaseScraper
from scrapers.utils import clean_text, generate_money_angle, make_description_ru
from database import Startup
from config import Config

logger = logging.getLogger(__name__)

TC_FEEDS = [
    "https://techcrunch.com/category/startups/feed/",
    "https://techcrunch.com/category/venture/feed/",
]


class TechCrunchScraper(BaseScraper):
    name = "TechCrunch"

    def scrape(self) -> list[Startup]:
        logger.info("Scraping TechCrunch RSS feeds...")
        startups: list[Startup] = []
        seen_urls: set[str] = set()

        for feed_url in TC_FEEDS:
            try:
                feed = feedparser.parse(feed_url, agent=Config.USER_AGENT)

                if feed.bozo and not feed.entries:
                    logger.warning(f"TechCrunch feed error for {feed_url}: {feed.bozo_exception}")
                    continue

                for entry in feed.entries[:20]:
                    try:
                        title = entry.get("title", "").strip()
                        link = entry.get("link", "").strip()
                        summary = entry.get("summary", "") or entry.get("description", "")

                        if not title or not link or link in seen_urls:
                            continue
                        seen_urls.add(link)

                        # Filter: only keep entries likely about a specific startup
                        # Skip pure opinion/analysis articles
                        lower_title = title.lower()
                        startup_signals = [
                            "launch", "raises", "funding", "seed",
                            "series", "backed", "startup", "announces",
                            "introduces", "unveils", "releases", "debuts",
                            "million", "billion", "round",
                        ]
                        if not any(sig in lower_title for sig in startup_signals):
                            # Also check summary
                            lower_summary = summary.lower()
                            if not any(sig in lower_summary for sig in startup_signals):
                                continue

                        desc = make_description_ru(title, clean_text(summary))
                        angle = generate_money_angle(title, summary)

                        startups.append(Startup(
                            name=title,
                            url=link,
                            description=desc,
                            money_angle=angle,
                            source=self.name,
                        ))
                    except Exception as e:
                        logger.warning(f"Error parsing TC entry: {e}")
                        continue

            except Exception as e:
                logger.error(f"Failed to fetch TechCrunch feed {feed_url}: {e}")

        logger.info(f"TechCrunch: found {len(startups)} startup entries")
        return startups
