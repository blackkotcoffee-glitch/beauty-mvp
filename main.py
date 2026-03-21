"""AI administrator for beauty studio."""

from telegram.ext import Application, MessageHandler, CommandHandler, filters
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN не найден")

async def start(update, context):
    name = update.effective_user.first_name
    await update.message.reply_text(
        f"Привет, {name}! Я администратор студии Коради. Чем могу помочь?"
    )

async def handle_message(update, context):
    text = update.message.text
    name = update.effective_user.first_name
    await update.message.reply_text(
        f"{name}, вы написали: {text}"
    )

def main():
    app = (
        Application.builder()
        .token(TOKEN)
        .proxy("http://127.0.0.1:12334")
        .get_updates_proxy("http://127.0.0.1:12334")
        .build()
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
