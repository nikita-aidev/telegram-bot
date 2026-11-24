"""
Подключение к ИИ через Groq.

У Groq API устроен так же, как у OpenAI, поэтому позже можно переключиться
на другой сервис (OpenRouter, OpenAI, Claude через совместимый шлюз),
поменяв только AI_BASE_URL, AI_MODEL и ключ в настройках.
"""

import logging
import os
import time
from collections import defaultdict, deque

import aiohttp

import content

API_KEY = os.getenv("GROQ_API_KEY", "").strip()
BASE_URL = os.getenv("AI_BASE_URL", "https://api.groq.com/openai/v1").strip().rstrip("/")
# gpt-oss-120b выбрана по тесту: отвечает на языке собеседника, коротко и по делу, < 1 сек.
# Список моделей Groq: https://console.groq.com/docs/models
MODEL = (os.getenv("AI_MODEL") or "openai/gpt-oss-120b").strip()
PROXY = (os.getenv("PROXY") or "").strip() or None  # только для запуска на вашем компьютере

ENABLED = bool(API_KEY)

# Ограничения, чтобы один посетитель не потратил весь бесплатный лимит
MAX_QUESTION_CHARS = 1000      # длинные вопросы обрезаем
MAX_ANSWER_TOKENS = 600        # ответ — не длиннее ~2–3 абзацев
HISTORY_MESSAGES = 6           # сколько последних реплик ИИ «помнит» в разговоре
USER_LIMIT_PER_HOUR = 20       # сколько вопросов в час может задать один человек

_user_requests: dict[int, deque] = defaultdict(deque)


class AIError(Exception):
    """Понятная ошибка, текст которой можно показать посетителю."""


def check_rate_limit(user_id: int) -> bool:
    """True — можно задать вопрос, False — человек исчерпал лимит на этот час."""
    now = time.time()
    q = _user_requests[user_id]
    while q and now - q[0] > 3600:
        q.popleft()
    if len(q) >= USER_LIMIT_PER_HOUR:
        return False
    q.append(now)
    return True


async def ask(question: str, history: list[dict]) -> str:
    """Отправляем вопрос ИИ вместе с краткой историей разговора и получаем ответ."""
    messages = [{"role": "system", "content": content.AI_SYSTEM_PROMPT}]
    messages += history[-HISTORY_MESSAGES:]
    messages.append({"role": "user", "content": question[:MAX_QUESTION_CHARS]})

    payload = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": MAX_ANSWER_TOKENS,
        "temperature": 0.6,
    }
    # «Думающие» модели: просим думать недолго и не показывать размышления посетителю
    if "gpt-oss" in MODEL:
        payload["reasoning_effort"] = "low"
    elif "qwen3" in MODEL:
        payload["reasoning_format"] = "hidden"
    headers = {"Authorization": f"Bearer {API_KEY}"}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{BASE_URL}/chat/completions",
                json=payload,
                headers=headers,
                proxy=PROXY,
                timeout=aiohttp.ClientTimeout(total=45),
            ) as r:
                data = await r.json(content_type=None)
                if r.status == 429:
                    raise AIError(content.AI_BUSY)
                if r.status >= 400:
                    logging.error("ИИ вернул ошибку %s: %s", r.status, str(data)[:300])
                    raise AIError(content.AI_ERROR)
                return data["choices"][0]["message"]["content"].strip()
    except AIError:
        raise
    except Exception as e:
        logging.error("Не удалось обратиться к ИИ: %s", e)
        raise AIError(content.AI_ERROR) from e
