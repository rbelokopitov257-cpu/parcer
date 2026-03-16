"""Utility helpers shared across scrapers — Russian text generation, cleaning."""

import re
import logging

logger = logging.getLogger(__name__)


def clean_text(text: str, max_len: int = 300) -> str:
    """Strip HTML, normalize whitespace, truncate."""
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > max_len:
        text = text[: max_len - 1].rsplit(" ", 1)[0] + "…"
    return text


def make_description_ru(title: str, summary: str) -> str:
    """Create a short Russian description from English title + summary."""
    # We keep it bilingual-friendly: short English context + Russian wrapper
    summary = clean_text(summary, 200)
    if not summary:
        return f"Новый проект: {title}"
    return summary


# Keyword → money-angle mapping (Russian)
_MONEY_ANGLES: list[tuple[list[str], str]] = [
    (
        ["api", "sdk", "developer", "integration", "platform"],
        "Можно строить продукты поверх их API/платформы и продавать как SaaS-решение.",
    ),
    (
        ["ai", "gpt", "llm", "machine learning", "artificial intelligence", "ml"],
        "AI-инструмент — можно создавать нишевые решения на его базе или предлагать настройку бизнесам.",
    ),
    (
        ["nocode", "no-code", "low-code", "builder", "template", "website builder"],
        "Можно делать и продавать готовые шаблоны, или предлагать услуги по настройке клиентам.",
    ),
    (
        ["analytics", "data", "dashboard", "metrics", "tracking"],
        "Можно стать консультантом по аналитике, помогая бизнесам внедрять этот инструмент.",
    ),
    (
        ["marketplace", "shop", "ecommerce", "e-commerce", "store"],
        "Можно использовать как платформу для продаж или делать интеграции для продавцов.",
    ),
    (
        ["design", "figma", "ui", "ux", "creative"],
        "Можно продавать дизайн-услуги или шаблоны, используя этот инструмент.",
    ),
    (
        ["finance", "fintech", "payment", "banking", "crypto", "trading"],
        "Финтех-ниша — можно стать партнёром/реферером или строить доп. сервисы для пользователей.",
    ),
    (
        ["automation", "workflow", "zapier", "automate", "bot"],
        "Можно продавать готовые автоматизации или настраивать их для бизнесов как услугу.",
    ),
    (
        ["open source", "github", "self-hosted"],
        "Open-source — можно предлагать хостинг, поддержку и кастомизацию как managed-сервис.",
    ),
    (
        ["education", "course", "learn", "tutorial"],
        "Можно создавать обучающий контент вокруг продукта или стать партнёром по реферальной программе.",
    ),
    (
        ["social", "community", "chat", "messaging"],
        "Можно строить нишевые сообщества на базе платформы или монетизировать через рекламу.",
    ),
    (
        ["productivity", "task", "project", "management", "todo", "notion"],
        "Можно продавать шаблоны, обучение и консалтинг по внедрению в команды.",
    ),
    (
        ["video", "stream", "media", "content", "creator"],
        "Контент-ниша — можно монетизировать через партнёрки, обзоры и создание контента.",
    ),
    (
        ["health", "fitness", "wellness", "medical"],
        "Здоровье — растущий рынок. Можно стать партнёром или строить доп. сервисы для аудитории.",
    ),
    (
        ["saas", "subscription", "tool"],
        "Можно стать реселлером, affiliate-партнёром или предлагать услуги настройки для клиентов.",
    ),
]

_DEFAULT_ANGLE = (
    "Изучить продукт и нишу — можно стать ранним affiliate-партнёром, "
    "создавать обзорный контент или предлагать услуги интеграции бизнесам."
)


def generate_money_angle(title: str, description: str) -> str:
    """Pick a money-angle suggestion based on keywords in the text."""
    combined = f"{title} {description}".lower()
    for keywords, angle in _MONEY_ANGLES:
        if any(kw in combined for kw in keywords):
            return angle
    return _DEFAULT_ANGLE
