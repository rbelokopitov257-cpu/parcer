"""Reddit — r/startups, r/entrepreneur, r/SideProject, r/YCombinator."""

import logging
import time
import requests
from scrapers import BaseScraper
from scrapers.utils import clean_text, generate_money_angle, make_description_ru
from database import Startup
from config import Config

logger = logging.getLogger(__name__)

SUBREDDITS = [
    "startups",
    "entrepreneur",
    "SideProject",
    "YCombinator",
]


class RedditScraper(BaseScraper):
    name = "Reddit"

    def scrape(self) -> list[Startup]:
        logger.info("Scraping Reddit subreddits...")
        startups: list[Startup] = []
        seen_urls: set[str] = set()

        for sub in SUBREDDITS:
            try:
                startups_from_sub = self._scrape_subreddit(sub, seen_urls)
                startups.extend(startups_from_sub)
                # Be polite — Reddit rate-limits aggressively
                time.sleep(2)
            except Exception as e:
                logger.error(f"Error scraping r/{sub}: {e}")

        logger.info(f"Reddit: found {len(startups)} posts total")
        return startups

    def _scrape_subreddit(self, subreddit: str, seen_urls: set[str]) -> list[Startup]:
        results: list[Startup] = []
        url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=25"

        try:
            resp = requests.get(
                url,
                headers={
                    "User-Agent": Config.USER_AGENT,
                },
                timeout=15,
            )

            if resp.status_code == 429:
                logger.warning(f"Reddit rate limited on r/{subreddit}, skipping")
                return []

            resp.raise_for_status()
            data = resp.json()

            posts = data.get("data", {}).get("children", [])

            for post in posts:
                try:
                    pdata = post.get("data", {})

                    # Skip stickied / mod posts
                    if pdata.get("stickied"):
                        continue

                    title = pdata.get("title", "").strip()
                    selftext = pdata.get("selftext", "")
                    post_url = pdata.get("url", "")
                    permalink = f"https://reddit.com{pdata.get('permalink', '')}"

                    # If it's a self-post, the URL is the reddit post itself
                    if pdata.get("is_self"):
                        link = permalink
                    else:
                        link = post_url or permalink

                    if not title or link in seen_urls:
                        continue

                    # Filter for startup-relevant posts
                    lower = f"{title} {selftext}".lower()
                    signals = [
                        "launch", "built", "created", "made", "building",
                        "side project", "my app", "my tool", "i made",
                        "i built", "just launched", "show", "feedback",
                        "startup", "mvp", "beta", "saas", "product",
                    ]
                    if not any(sig in lower for sig in signals):
                        continue

                    seen_urls.add(link)

                    desc = make_description_ru(title, clean_text(selftext, 200))
                    angle = generate_money_angle(title, selftext)

                    results.append(Startup(
                        name=title,
                        url=link,
                        description=desc,
                        money_angle=angle,
                        source=f"Reddit r/{subreddit}",
                    ))

                except Exception as e:
                    logger.warning(f"Error parsing Reddit post in r/{subreddit}: {e}")
                    continue

        except requests.RequestException as e:
            logger.error(f"Failed to fetch r/{subreddit}: {e}")

        logger.info(f"  r/{subreddit}: {len(results)} relevant posts")
        return results
