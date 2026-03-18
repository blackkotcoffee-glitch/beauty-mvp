"""AI agent for beauty."""

from dotenv import load_dotenv
import os
import requests
import json

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

print("\n--- Работа с Dict/List ---")

date = data["date"]
base = data["base"]
rates = data["rates"]

print(f"Дата обновления: {date}")
print(f"Базовая валюта: {base}")    

currencies = ["USD", "EUR", "CNY", "GBP"]

print("\nКурсы валют:")
for currency in currencies:
    rate = rates.get(currency, "не найден")
    print(f"  {currency}: {rate}")

print("\nВалюты дороже 0.01 к рублю:")
expensive = [c for c in currencies if rates.get(c, 0) > 0.01]
print(expensive)

json_string = json.dumps(data, indent=2, ensure_ascii=False)
print(f"\nПервые 100 символов JSON ответа:")
print(json_string[:100])
