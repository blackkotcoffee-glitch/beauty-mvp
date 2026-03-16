"""AI agent for beauty."""

from dotenv import load_dotenv
import os

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
DIKIDI_API_KEY = os.getenv("DIKIDI_API_KEY")

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN не найден")
if not CLAUDE_API_KEY:
    raise ValueError("CLAUDE_API_KEY не найден")
if not DIKIDI_API_KEY:
    raise ValueError("DIKIDI_API_KEY не найден")

print("All keys loaded successfully")
