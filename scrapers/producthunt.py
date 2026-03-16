"""Product Hunt — RSS feed scraper."""

import logging
import feedparser
from scrapers import BaseScraper
from scrapers.utils import clean_text, generate_money_angle, make_description_ru
from database import Startup
from config import Config

logger = logging.getLogger(__name__)

PH_FEED_URL = "https://www.producthunt.com/feed"


class ProductHuntScraper(BaseScraper):
    name = "Product Hunt"

    def scrape(self) -> list[Startup]:
        logger.info("Scraping Product Hunt RSS...")
        startups: list[Startup] = []

        try:
            feed = feedparser.parse(
                PH_FEED_URL,
                agent=Config.USER_AGENT,
            )

            if feed.bozo and not feed.entries:
                logger.warning(f"Product Hunt feed parse error: {feed.bozo_exception}")
                return []

            for entry in feed.entries[:40]:
                try:
                    title = entry.get("title", "").strip()
                    link = entry.get("link", "").strip()
                    summary = entry.get("summary", "") or entry.get("description", "")

                    if not title or not link:
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
                    logger.warning(f"Error parsing PH entry: {e}")
                    continue

        except Exception as e:
            logger.error(f"Failed to fetch Product Hunt feed: {e}")

        logger.info(f"Product Hunt: found {len(startups)} entries")
        return startups
