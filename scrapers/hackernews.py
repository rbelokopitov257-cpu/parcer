"""Hacker News — Show HN posts scraper."""

import logging
import requests
from scrapers import BaseScraper
from scrapers.utils import clean_text, generate_money_angle, make_description_ru
from database import Startup
from config import Config

logger = logging.getLogger(__name__)

SHOW_HN_URL = "https://hacker-news.firebaseio.com/v0/showstories.json"
ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json"
MAX_ITEMS = 30  # Check top 30 Show HN posts


class HackerNewsScraper(BaseScraper):
    name = "Hacker News (Show HN)"

    def scrape(self) -> list[Startup]:
        logger.info("Scraping Hacker News Show HN...")
        startups: list[Startup] = []

        try:
            resp = requests.get(
                SHOW_HN_URL,
                headers={"User-Agent": Config.USER_AGENT},
                timeout=15,
            )
            resp.raise_for_status()
            story_ids = resp.json()[:MAX_ITEMS]
        except Exception as e:
            logger.error(f"Failed to fetch Show HN list: {e}")
            return []

        for sid in story_ids:
            try:
                item = requests.get(
                    ITEM_URL.format(sid),
                    headers={"User-Agent": Config.USER_AGENT},
                    timeout=10,
                ).json()

                if not item or item.get("dead") or item.get("deleted"):
                    continue

                title = item.get("title", "")
                url = item.get("url") or f"https://news.ycombinator.com/item?id={sid}"
                text = item.get("text", "")

                # Clean up "Show HN:" prefix
                clean_title = title.replace("Show HN:", "").replace("Show HN –", "").strip()
                if not clean_title:
                    continue

                desc = make_description_ru(clean_title, text or title)
                angle = generate_money_angle(clean_title, text or title)

                startups.append(Startup(
                    name=clean_title,
                    url=url,
                    description=desc,
                    money_angle=angle,
                    source=self.name,
                ))

            except Exception as e:
                logger.warning(f"Error fetching HN item {sid}: {e}")
                continue

        logger.info(f"Hacker News: found {len(startups)} Show HN posts")
        return startups
