"""SQLite storage for deduplication — remembers every startup ever seen."""

import sqlite3
import os
import logging
from datetime import datetime, timezone
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class Startup:
    name: str
    url: str
    description: str
    money_angle: str
    source: str
    discovered_at: str = ""

    def __post_init__(self):
        if not self.discovered_at:
            self.discovered_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        return asdict(self)


class Database:
    def __init__(self, db_path: str):
        os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else ".", exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
        logger.info(f"Database initialized at {db_path}")

    def _create_tables(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS startups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE,
                description TEXT,
                money_angle TEXT,
                source TEXT,
                discovered_at TEXT,
                sent INTEGER DEFAULT 0
            )
        """)
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_url ON startups(url)
        """)
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_sent ON startups(sent)
        """)
        self.conn.commit()

    def is_seen(self, url: str) -> bool:
        """Check if a startup URL has already been recorded."""
        row = self.conn.execute(
            "SELECT 1 FROM startups WHERE url = ?", (url,)
        ).fetchone()
        return row is not None

    def add_startup(self, startup: Startup) -> bool:
        """Add a startup if it hasn't been seen before. Returns True if new."""
        if self.is_seen(startup.url):
            return False
        try:
            self.conn.execute(
                """INSERT INTO startups (name, url, description, money_angle, source, discovered_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (startup.name, startup.url, startup.description,
                 startup.money_angle, startup.source, startup.discovered_at),
            )
            self.conn.commit()
            logger.debug(f"New startup saved: {startup.name}")
            return True
        except sqlite3.IntegrityError:
            return False

    def get_unsent(self) -> list[Startup]:
        """Return all startups that haven't been sent yet."""
        rows = self.conn.execute(
            "SELECT name, url, description, money_angle, source, discovered_at "
            "FROM startups WHERE sent = 0 ORDER BY id"
        ).fetchall()
        return [Startup(**dict(r)) for r in rows]

    def mark_sent(self, urls: list[str]):
        """Mark a batch of startups as sent."""
        if not urls:
            return
        placeholders = ",".join("?" for _ in urls)
        self.conn.execute(
            f"UPDATE startups SET sent = 1 WHERE url IN ({placeholders})", urls
        )
        self.conn.commit()
        logger.info(f"Marked {len(urls)} startups as sent")

    def stats(self) -> dict:
        """Quick stats."""
        total = self.conn.execute("SELECT COUNT(*) FROM startups").fetchone()[0]
        unsent = self.conn.execute("SELECT COUNT(*) FROM startups WHERE sent=0").fetchone()[0]
        return {"total": total, "unsent": unsent}

    def close(self):
        self.conn.close()
