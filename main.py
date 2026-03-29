"""AI administrator for beauty studio Koradi."""

from telegram.ext import Application, MessageHandler, CommandHandler, filters
from dotenv import load_dotenv
import anthropic
import json
import re
import os
import asyncio
import logging
from database import init_db, save_message, get_history

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
ANTHROPIC_BASE_URL = os.getenv("ANTHROPIC_BASE_URL")

if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN не найден")
if not CLAUDE_API_KEY:
    raise ValueError("CLAUDE_API_KEY не найден")

claude = anthropic.AsyncAnthropic(
    api_key=CLAUDE_API_KEY,
    base_url=ANTHROPIC_BASE_URL
)

SYSTEM_PROMPT = """
Ты — администратор студии бровей и ресниц «Коради» (Москва).
Общайся с клиентами на «Вы», вежливо и коротко. Без эмодзи.

Адрес: Волгоградский просп., 32/5к1, корпус «Венеция», ЖК Метрополия, 6 этаж.
Как добраться: метро «Волгоградский проспект» (10 мин) или МЦК «Угрешская» (3 мин).
Режим работы: ежедневно по предварительной записи.
Телефон: +7 (915) 184-38-68

Прайс услуг:
НАРАЩИВАНИЕ РЕСНИЦ:
- Classic / 1D-1.5D — от 3300 руб, 1.5 часа
- 2D-2.5D — от 3600 руб, 2 часа
- 3D-3.5D — от 3900 руб, 2 часа
- Неполное / уголки — от 3000 руб, 1 час
- Аниме / Кайли / Лами — 3600 руб, 2 часа
- Мега-объем / Виспи — 3900 руб, 2 часа

ЛАМИНИРОВАНИЕ РЕСНИЦ:
- Ламинирование (окрашивание и уход входит) — 3000 руб, 1.5 часа
- Ламинирование нижних ресниц — 1000 руб, 1 час
- Окрашивание ресниц — 800 руб, 30 мин

ОФОРМЛЕНИЕ БРОВЕЙ:
- Коррекция бровей — 1500 руб, 45 мин
- Осветление/окрашивание — 1500 руб, 30 мин
- Оформление бровей (окрашивание и коррекция) — 2400 руб, 1 час
- Мужское оформление бровей — от 1500 руб, 1 час

ДОЛГОВРЕМЕННАЯ УКЛАДКА БРОВЕЙ:
- Укладка (уход входит) — 2000 руб, 40 мин
- Укладка + одиночная процедура — 2500 руб, 1 час
- Укладка с оформлением (полный комплекс) — 3000 руб, 1.5 часа

КОМПЛЕКСЫ:
- Комплекс Lami (ламинирование + укладка бровей) — 4700 руб, 1.75 часа
- Комплекс Maxi (оформление бровей + ламинирование) — 5100 руб, 2.25 часа
- Комплекс Mini (оформление бровей + окрашивание ресниц) — 3000 руб, 1.25 часа

МАКИЯЖ:
- Дневной / nude — 3500 руб, 1.5 часа
- Свадебный / вечерний — 4500 руб, 1.5 часа
- Полный образ (макияж + укладка) — от 7000 руб, 2.5 часа
- Укладка локоны/пучок/хвост — 3000 руб, 1.5 часа

ДОПОЛНИТЕЛЬНЫЕ УСЛУГИ:
- Ботокс для бровей — 1000 руб, 30 мин
- Удаление нежелательного волоса (1 зона) — 300 руб, 15 мин

Мастера:
- Алина — основатель, топ-мастер (все услуги)
- Елена — мастер по наращиванию ресниц
- Славяна — мастер по трендовым наращиваниям

Правила:
- Никогда не придумывай услуги или цены которых нет в прайсе
- Спорные вопросы передавай мастеру: +7 (915) 184-38-68
- Если вопрос не про студию — вежливо скажи что можешь помочь только с вопросами о студии
- С детьми приходить можно

Формат ответа — ТОЛЬКО JSON без markdown и пояснений:
{
    "intent": "price_question" | "booking" | "faq" | "cancel" | "greeting" | "unknown",
    "service": "название услуги или null",
    "reply": "текст ответа клиенту на русском, вежливо, на Вы, без эмодзи, максимум 3 предложения"
}
"""

def parse_json_response(text: str) -> dict:
    """Безопасно парсим JSON из ответа Claude."""
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    text = text.strip()

    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        text = match.group()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        logger.error(f"Ошибка парсинга JSON: {text[:100]}")
        return {
            "intent": "unknown",
            "service": None,
            "reply": "Извините, не смогла обработать запрос. Попробуйте написать иначе."
        }


def handle_intent(data: dict) -> str:
    """Формируем финальный ответ на основе намерения."""
    intent = data.get("intent", "unknown")
    reply = data.get("reply", "")

    if intent == "booking":
        reply += "\n\nЗаписаться: https://dikidi.net/koradi"

    elif intent == "cancel":
        reply += "\n\nДля отмены свяжитесь с нами: +7 (915) 184-38-68"

    return reply


async def get_claude_response(user_id: int, user_message: str) -> str:
    """Отправить сообщение в Claude и получить ответ."""
    await save_message(user_id, "user", user_message)
    logger.info(f"Пользователь {user_id}: {user_message[:50]}")
    
    history = await get_history(user_id)

    response = await claude.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=256,
        system=SYSTEM_PROMPT,
        messages=history,
        stream=False
    )

    raw_reply = next(
        block.text for block in response.content
        if block.type == "text"
    )

    await save_message(user_id, "assistant", raw_reply)

    data = parse_json_response(raw_reply) 
    logger.info(f"Intent: {data.get('intent')}, service: {data.get('service')}") 
    return handle_intent(data)


async def start(update, context):
    """Обработчик команды /start."""
    name = update.effective_user.first_name
    await update.message.reply_text(
        f"Здравствуйте, {name}! Я администратор студии бровей и ресниц «Коради». Чем могу помочь?"
    )

async def keep_typing(context, chat_id):
    """Показывать 'печатает...' каждые 4 секунды."""
    while True:
        await context.bot.send_chat_action(
            chat_id=chat_id,
            action="typing"
        )
        await asyncio.sleep(4)

async def handle_message(update, context):
    """Обработчик входящих сообщений."""
    user_id = update.effective_user.id
    user_text = update.message.text
    chat_id = update.effective_chat.id

    typing_task = asyncio.create_task(keep_typing(context, chat_id))
    reply = await get_claude_response(user_id, user_text)
    typing_task.cancel()

    await update.message.reply_text(reply)


def main():
    """Запуск бота."""
    app = (
        Application.builder()
        .token(TOKEN)
        .proxy("http://127.0.0.1:12334")
        .get_updates_proxy("http://127.0.0.1:12334")
        .build()
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    asyncio.run(init_db())
    logger.info("Бот запущен")
    app.run_polling()


if __name__ == "__main__":
    main()
