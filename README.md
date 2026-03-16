# 🚀 StartupMonitor Bot

Автоматический Telegram-бот, который каждый день собирает новые стартапы с Hacker News, Product Hunt, TechCrunch и Reddit, и отправляет дайджест в Telegram на русском языке.

---

## Возможности

- **4 источника**: Hacker News (Show HN), Product Hunt RSS, TechCrunch RSS, Reddit (4 сабреддита)
- **Дедупликация**: SQLite база — каждый стартап отправляется только один раз
- **Telegram дайджест**: красиво отформатированные сообщения на русском
- **Docker**: развёртывается одной командой где угодно
- **Без платных API**: нужен только Telegram Bot Token

---

## Быстрый старт (5 минут)

### Шаг 1. Создай Telegram-бота

1. Открой Telegram, найди **@BotFather**
2. Отправь `/newbot`
3. Придумай имя бота (например: `Мой Стартап Монитор`)
4. Придумай username (например: `my_startup_monitor_bot`)
5. BotFather даст тебе **токен** вида `7123456789:AAH...` — **сохрани его**

### Шаг 2. Узнай свой Chat ID

1. Найди в Telegram бота **@userinfobot**
2. Отправь ему любое сообщение
3. Он ответит твоим **Chat ID** (число вроде `123456789`) — **сохрани его**

**Для группового чата**: добавь бота в группу, отправь сообщение, затем открой в браузере:
```
https://api.telegram.org/bot<ТВОЙ_ТОКЕН>/getUpdates
```
Найди `"chat":{"id":-100...}` — это Chat ID группы (со знаком минус).

### Шаг 3. Настрой и запусти

```bash
# Клонируй репозиторий
git clone <твой-репо>
cd startup-monitor

# Создай .env файл
cp .env.example .env

# Впиши свои данные
nano .env
```

Заполни `.env`:
```env
TELEGRAM_BOT_TOKEN=7123456789:AAHxxx...
TELEGRAM_CHAT_ID=123456789
DIGEST_HOUR=9
DIGEST_MINUTE=0
RUN_ON_START=true
LOG_LEVEL=INFO
```

**Запуск через Docker (рекомендуется):**
```bash
docker-compose up -d
```

**Запуск без Docker:**
```bash
pip install -r requirements.txt
python main.py
```

---

## Деплой на Railway (бесплатно)

Railway даёт $5 кредитов в месяц — хватит с запасом для этого бота.

### Шаг 1. Подготовь GitHub-репо

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/<user>/<repo>.git
git push -u origin main
```

### Шаг 2. Railway

1. Зайди на [railway.app](https://railway.app) и авторизуйся через GitHub
2. Нажми **New Project** → **Deploy from GitHub repo**
3. Выбери свой репозиторий
4. Railway автоматически обнаружит Dockerfile

### Шаг 3. Переменные окружения

В Railway Settings → Variables добавь:

| Variable | Value |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Твой токен от BotFather |
| `TELEGRAM_CHAT_ID` | Твой Chat ID |
| `DIGEST_HOUR` | `9` (или другое время UTC) |
| `DIGEST_MINUTE` | `0` |
| `RUN_ON_START` | `true` |
| `DB_PATH` | `/app/data/startups.db` |

### Шаг 4. Постоянное хранилище

В Railway → сервис → Settings → добавь **Volume**:
- Mount path: `/app/data`

Это сохранит SQLite базу между рестартами.

### Шаг 5. Готово!

Railway сам соберёт и запустит контейнер. Бот пришлёт тебе сообщение в Telegram о запуске.

---

## Структура проекта

```
startup-monitor/
├── main.py              # Оркестратор: scheduler + pipeline
├── config.py            # Загрузка настроек из .env
├── database.py          # SQLite: хранение и дедупликация
├── notifier.py          # Форматирование и отправка в Telegram
├── scrapers/
│   ├── __init__.py      # Базовый класс + реестр скраперов
│   ├── utils.py         # Утилиты: тексты, money-angle
│   ├── hackernews.py    # Hacker News Show HN
│   ├── producthunt.py   # Product Hunt RSS
│   ├── techcrunch.py    # TechCrunch RSS
│   └── reddit.py        # Reddit (4 сабреддита)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

---

## Настройка времени дайджеста

В `.env` файле:
```env
DIGEST_HOUR=9     # Час (UTC, 24ч формат)
DIGEST_MINUTE=0   # Минуты
```

Москва = UTC+3, значит `DIGEST_HOUR=6` отправит дайджест в 9:00 по Москве.

---

## FAQ

**Q: Бот не отправляет сообщения?**
Убедись, что ты написал боту `/start` в Telegram хотя бы раз.

**Q: Как добавить новый источник?**
Создай файл в `scrapers/`, наследуй от `BaseScraper`, реализуй метод `scrape()`, добавь в `ALL_SCRAPERS` в `__init__.py`.

**Q: Как часто можно запускать?**
Источники бесплатные, но Reddit агрессивно лимитирует. Раз в день — оптимально.

**Q: Как сбросить базу и начать заново?**
Удали файл `data/startups.db` и перезапусти бота.
