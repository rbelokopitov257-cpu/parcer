"""Telegram notifier — formats the daily digest and sends it."""

import logging
import requests
from database import Startup
from config import Config

logger = logging.getLogger(__name__)

TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"
MAX_MESSAGE_LENGTH = 4000  # Telegram limit is 4096; leave margin


def _format_entry(s: Startup) -> str:
    """Format a single startup entry in Russian."""
    return (
        f"🚀 <b>{_esc(s.name)}</b>\n"
        f"📌 Что делает: {_esc(s.description)}\n"
        f"💰 Как заработать: {_esc(s.money_angle)}\n"
        f"🔗 {_esc(s.url)}\n"
        f"📡 Источник: {_esc(s.source)}"
    )


def _esc(text: str) -> str:
    """Escape HTML special characters for Telegram."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _build_messages(startups: list[Startup]) -> list[str]:
    """Split startups into message chunks that fit Telegram limits."""
    if not startups:
        return []

    header = (
        "📋 <b>Дайджест новых стартапов</b>\n"
        f"Найдено за сегодня: <b>{len(startups)}</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
    )

    messages: list[str] = []
    current = header

    for i, s in enumerate(startups):
        entry = _format_entry(s)
        separator = "\n\n━━━━━━━━━━━━━━━━━━━━━\n\n" if i > 0 else ""
        block = separator + entry

        if len(current) + len(block) > MAX_MESSAGE_LENGTH:
            messages.append(current)
            current = f"📋 <b>Дайджест (продолжение)</b>\n\n{entry}"
        else:
            current += block

    if current:
        messages.append(current)

    return messages


def send_digest(startups: list[Startup]) -> bool:
    """Send the daily digest to Telegram. Returns True on success."""
    if not startups:
        logger.info("No new startups to send — skipping digest")
        return True

    messages = _build_messages(startups)
    url = TELEGRAM_API.format(token=Config.TELEGRAM_BOT_TOKEN)
    success = True

    for i, text in enumerate(messages):
        try:
            resp = requests.post(
                url,
                json={
                    "chat_id": Config.TELEGRAM_CHAT_ID,
                    "text": text,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": True,
                },
                timeout=30,
            )
            if resp.status_code == 200:
                logger.info(f"Message {i+1}/{len(messages)} sent OK")
            else:
                logger.error(f"Telegram API error {resp.status_code}: {resp.text}")
                success = False
        except requests.RequestException as e:
            logger.error(f"Failed to send message {i+1}: {e}")
            success = False

    return success


def send_status(text: str):
    """Send a short status/error message to Telegram."""
    url = TELEGRAM_API.format(token=Config.TELEGRAM_BOT_TOKEN)
    try:
        requests.post(
            url,
            json={
                "chat_id": Config.TELEGRAM_CHAT_ID,
                "text": f"ℹ️ StartupMonitor: {text}",
                "parse_mode": "HTML",
            },
            timeout=15,
        )
    except Exception as e:
        logger.error(f"Failed to send status: {e}")
