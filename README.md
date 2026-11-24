# Telegram-бот визитка — Никита, AI Engineer

Бот рассказывает обо мне, показывает проекты и принимает заявки от работодателей и заказчиков.
Заявки сразу приходят мне в Telegram.

**Стек:** Python 3.13, aiogram 3, aiohttp. Работает в облаке на Render (webhook).

## Возможности
- Меню на inline-кнопках: «Обо мне», «Навыки», «Проекты», ссылки на сайт, Telegram и GitHub
- Пошаговая заявка (имя → контакт → задача) с пересылкой владельцу
- Тексты и проекты вынесены в `content.py` — меняются без правки логики
- Два режима запуска: polling (локально) и webhook (в облаке), выбирается автоматически
- Защита webhook секретным токеном

## Запуск локально
```bash
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
copy .env.example .env   # и впишите BOT_TOKEN
.venv\Scripts\python bot.py
```

## Переменные окружения
| Переменная | Зачем |
|---|---|
| `BOT_TOKEN` | токен от @BotFather |
| `ADMIN_ID` | ваш Telegram ID — куда слать заявки (узнать: `/id` в боте) |
| `WEBHOOK_SECRET` | любая случайная строка, защищает webhook |
| `PROXY` | прокси, если Telegram недоступен напрямую (только локально) |

На Render адрес сервиса (`RENDER_EXTERNAL_URL`) подставляется автоматически.
