"""AI agent for beauty."""

from dotenv import load_dotenv
import os
import requests

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

url = "https://api.exchangerate-api.com/v4/latest/RUB"

response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    print("Статус:", response.status_code)
    print("Базовая валюта:", data["base"])
    print("Курс USD:", data["rates"]["USD"])
    print("Курс EUR:", data["rates"]["EUR"])
else:
    print("Ошибка:", response.status_code)
    

