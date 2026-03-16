#!/usr/bin/env python3
"""
StartupMonitor — daily startup digest bot.

Scrapes HN, Product Hunt, TechCrunch, Reddit → deduplicates via SQLite
→ sends a Telegram digest once per day in Russian.
"""

import logging
import sys
import time
import schedule

from config import Config
from database import Database
from notifier import send_digest, send_status
from scrapers import ALL_SCRAPERS

# ── Logging ──────────────────────────────────────────────────────────────

logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL, logging.INFO),
    format="%(asctime)s │ %(levelname)-7s │ %(name)-20s │ %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("main")


# ── Core pipeline ────────────────────────────────────────────────────────

def run_pipeline(db: Database):
    """Run all scrapers → store new startups → send digest."""
    logger.info("=" * 60)
    logger.info("Pipeline started")

    total_new = 0
    total_found = 0
    errors: list[str] = []

    # 1. Scrape all sources
    for scraper_cls in ALL_SCRAPERS:
        scraper_name = scraper_cls.name
        try:
            scraper = scraper_cls()
            startups = scraper.scrape()
            total_found += len(startups)

            new_count = 0
            for s in startups:
                if db.add_startup(s):
                    new_count += 1

            total_new += new_count
            logger.info(f"  {scraper_name}: {len(startups)} found, {new_count} new")

        except Exception as e:
            msg = f"{scraper_name} failed: {e}"
            logger.error(msg, exc_info=True)
            errors.append(msg)

    logger.info(f"Scraping done: {total_found} total, {total_new} new")

    # 2. Send digest of all unsent startups
    unsent = db.get_unsent()
    if unsent:
        logger.info(f"Sending digest with {len(unsent)} startups...")
        success = send_digest(unsent)
        if success:
            db.mark_sent([s.url for s in unsent])
            logger.info("Digest sent successfully!")
        else:
            logger.error("Failed to send some digest messages")
    else:
        logger.info("No new startups to send today")

    # 3. Log errors summary
    if errors:
        err_text = "\n".join(f"⚠️ {e}" for e in errors)
        logger.warning(f"Errors during run:\n{err_text}")

    stats = db.stats()
    logger.info(f"DB stats: {stats['total']} total, {stats['unsent']} unsent")
    logger.info("Pipeline finished")
    logger.info("=" * 60)


# ── Entrypoint ───────────────────────────────────────────────────────────

def main():
    # Validate config
    config_errors = Config.validate()
    if config_errors:
        for e in config_errors:
            logger.error(f"Config error: {e}")
        logger.error("Fix .env file and restart. See .env.example for reference.")
        sys.exit(1)

    logger.info("StartupMonitor starting up")
    logger.info(f"Digest scheduled at {Config.DIGEST_HOUR:02d}:{Config.DIGEST_MINUTE:02d} UTC")
    logger.info(f"Database: {Config.DB_PATH}")

    db = Database(Config.DB_PATH)

    # Run immediately on start if configured
    if Config.RUN_ON_START:
        logger.info("RUN_ON_START=true — running pipeline now")
        run_pipeline(db)

    # Schedule daily run
    digest_time = f"{Config.DIGEST_HOUR:02d}:{Config.DIGEST_MINUTE:02d}"
    schedule.every().day.at(digest_time).do(run_pipeline, db=db)
    logger.info(f"Scheduled daily digest at {digest_time} UTC")

    # Send startup notification
    send_status(
        f"Бот запущен ✅\n"
        f"Дайджест каждый день в {digest_time} UTC\n"
        f"Источники: HN, Product Hunt, TechCrunch, Reddit"
    )

    # Main loop
    try:
        while True:
            schedule.run_pending()
            time.sleep(30)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        db.close()
        logger.info("Goodbye!")


if __name__ == "__main__":
    main()
