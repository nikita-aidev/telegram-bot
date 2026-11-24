"""
Telegram-бот визитка Никиты.

Запуск:  python bot.py
Настройки (токен и ваш ID) лежат в файле .env — см. .env.example
"""

import asyncio
import html
import logging
import os

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    BotCommand,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from dotenv import load_dotenv

import content

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
ADMIN_ID = os.getenv("ADMIN_ID", "").strip()  # куда присылать заявки (ваш Telegram ID)
# Прокси (VPN). Берём из .env, а если там пусто — из настроек системы (HTTPS_PROXY)
PROXY = (os.getenv("PROXY") or os.getenv("HTTPS_PROXY") or os.getenv("HTTP_PROXY") or "").strip()

router = Router()


# =====================================================
#  КНОПКИ
# =====================================================
def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👤 Обо мне", callback_data="about"),
            InlineKeyboardButton(text="🛠 Навыки", callback_data="skills"),
        ],
        [
            InlineKeyboardButton(text="🚀 Проекты", callback_data="projects"),
            InlineKeyboardButton(text="🌐 Сайт", url=content.SITE_URL),
        ],
        [InlineKeyboardButton(text="✉️ Оставить заявку", callback_data="order")],
        [
            InlineKeyboardButton(text="💬 Telegram", url=content.TELEGRAM_URL),
            InlineKeyboardButton(text="💻 GitHub", url=content.GITHUB_URL),
        ],
    ])


def back_button() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="menu")],
    ])


def cancel_button() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✖️ Отменить", callback_data="cancel")],
    ])


def projects_text() -> str:
    lines = ["🚀 <b>Проекты</b>\n"]
    for i, p in enumerate(content.PROJECTS, start=1):
        lines.append(f"<b>{i}. {p['title']}</b>\n{p['description']}")
        if p.get("link"):
            lines.append(f'🔗 <a href="{p["link"]}">Открыть</a>')
        lines.append("")
    return "\n".join(lines)


# =====================================================
#  КОМАНДЫ
# =====================================================
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(content.WELCOME, reply_markup=main_menu())


@router.message(Command("menu"))
async def cmd_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(content.WELCOME, reply_markup=main_menu())


@router.message(Command("id"))
async def cmd_id(message: Message):
    # Помогает узнать свой Telegram ID, чтобы вписать его в .env как ADMIN_ID
    await message.answer(f"Ваш Telegram ID: <code>{message.from_user.id}</code>")


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(content.ORDER_CANCELLED, reply_markup=main_menu())


# =====================================================
#  РАЗДЕЛЫ МЕНЮ
# =====================================================
async def show(callback: CallbackQuery, text: str, markup: InlineKeyboardMarkup):
    """Меняем текст текущего сообщения, чтобы чат не засорялся."""
    await callback.message.edit_text(text, reply_markup=markup, disable_web_page_preview=True)
    await callback.answer()


@router.callback_query(F.data == "menu")
async def cb_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await show(callback, content.WELCOME, main_menu())


@router.callback_query(F.data == "about")
async def cb_about(callback: CallbackQuery):
    await show(callback, content.ABOUT, back_button())


@router.callback_query(F.data == "skills")
async def cb_skills(callback: CallbackQuery):
    await show(callback, content.SKILLS, back_button())


@router.callback_query(F.data == "projects")
async def cb_projects(callback: CallbackQuery):
    await show(callback, projects_text(), back_button())


# =====================================================
#  ЗАЯВКА (бот задаёт 3 вопроса по очереди)
# =====================================================
class Order(StatesGroup):
    name = State()
    contact = State()
    task = State()


@router.callback_query(F.data == "order")
async def cb_order(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Order.name)
    await show(callback, content.ORDER_START, cancel_button())


@router.callback_query(F.data == "cancel")
async def cb_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await show(callback, content.ORDER_CANCELLED + "\n\n" + content.WELCOME, main_menu())


@router.message(Order.name, F.text)
async def order_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Order.contact)
    await message.answer(content.ORDER_ASK_CONTACT, reply_markup=cancel_button())


@router.message(Order.contact, F.text)
async def order_contact(message: Message, state: FSMContext):
    await state.update_data(contact=message.text)
    await state.set_state(Order.task)
    await message.answer(content.ORDER_ASK_TASK, reply_markup=cancel_button())


@router.message(Order.task, F.text)
async def order_task(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    await state.clear()

    user = message.from_user
    username = f"@{user.username}" if user.username else "нет username"
    # html.escape — чтобы текст от посетителя не сломал оформление сообщения
    report = (
        "📩 <b>Новая заявка!</b>\n\n"
        f"<b>Имя:</b> {html.escape(data['name'])}\n"
        f"<b>Контакт:</b> {html.escape(data['contact'])}\n"
        f"<b>Задача:</b> {html.escape(message.text)}\n\n"
        f"<b>Telegram:</b> {username} (ID <code>{user.id}</code>)"
    )

    if ADMIN_ID:
        try:
            await bot.send_message(int(ADMIN_ID), report)
        except Exception as e:  # например, вы ещё ни разу не писали боту
            logging.error("Не удалось отправить заявку владельцу: %s", e)
    else:
        logging.warning("ADMIN_ID не задан в .env — заявка только в логе:\n%s", report)

    await message.answer(content.ORDER_DONE, reply_markup=main_menu())


@router.message(StateFilter(Order))
async def order_not_text(message: Message):
    # Если в заявке прислали стикер, фото и т. п.
    await message.answer(content.ORDER_NEED_TEXT)


@router.message()
async def fallback(message: Message):
    # На любое другое сообщение показываем меню
    await message.answer(content.WELCOME, reply_markup=main_menu())


# =====================================================
#  ЗАПУСК
#  Два режима:
#   • на вашем компьютере — «polling» (бот сам спрашивает Telegram о новых сообщениях);
#   • в облаке (Render) — «webhook» (Telegram сам присылает сообщения боту на его адрес).
#  Режим выбирается автоматически: если есть адрес сервера (RENDER_EXTERNAL_URL
#  или WEBHOOK_URL) — webhook, иначе polling.
# =====================================================
WEBHOOK_BASE = (os.getenv("WEBHOOK_URL") or os.getenv("RENDER_EXTERNAL_URL") or "").strip().rstrip("/")
WEBHOOK_PATH = "/webhook"
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "").strip()  # защита: чужие не смогут слать боту фальшивые сообщения
PORT = int(os.getenv("PORT", "8080"))


def create_bot() -> Bot:
    if not BOT_TOKEN:
        raise SystemExit("❌ Не найден BOT_TOKEN. Создайте файл .env по образцу .env.example")
    session = AiohttpSession(proxy=PROXY) if PROXY else AiohttpSession()
    if PROXY:
        logging.info("Подключаюсь к Telegram через прокси %s", PROXY)
    return Bot(BOT_TOKEN, session=session, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


async def prepare(bot: Bot):
    """То, что делаем при каждом запуске. Ошибки здесь не останавливают бота."""
    try:
        await bot.set_my_commands([
            BotCommand(command="start", description="Главное меню"),
            BotCommand(command="cancel", description="Отменить заявку"),
        ])
    except Exception as e:
        logging.warning("Не удалось обновить меню команд (не критично): %s", e)
    if not ADMIN_ID:
        logging.warning("ADMIN_ID не задан — заявки не будут приходить вам в Telegram")


async def run_polling():
    bot = create_bot()
    dp = Dispatcher()
    dp.include_router(router)
    await prepare(bot)
    await bot.delete_webhook(drop_pending_updates=False)  # на случай, если раньше бот работал в облаке
    logging.info("Бот запущен (polling). Остановить: Ctrl+C")
    await dp.start_polling(bot)


def run_webhook():
    from aiohttp import web
    from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

    bot = create_bot()
    dp = Dispatcher()
    dp.include_router(router)

    async def on_startup(bot: Bot):
        await prepare(bot)
        await bot.set_webhook(
            f"{WEBHOOK_BASE}{WEBHOOK_PATH}",
            secret_token=WEBHOOK_SECRET or None,
            allowed_updates=dp.resolve_used_update_types(),
        )
        logging.info("Бот запущен (webhook): %s%s", WEBHOOK_BASE, WEBHOOK_PATH)

    dp.startup.register(on_startup)

    async def health(request):
        # Страница-проверка: хостинг и вы можете открыть адрес и увидеть, что бот жив
        return web.Response(text="Bot is running ✅")

    app = web.Application()
    app.router.add_get("/", health)
    SimpleRequestHandler(dispatcher=dp, bot=bot, secret_token=WEBHOOK_SECRET or None).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    web.run_app(app, host="0.0.0.0", port=PORT)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    if WEBHOOK_BASE:
        run_webhook()
    else:
        asyncio.run(run_polling())
