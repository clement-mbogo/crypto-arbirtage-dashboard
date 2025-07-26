import requests
import json

# Load Telegram config
with open("settings.json", "r") as f:
    settings = json.load(f)

TELEGRAM_TOKEN = settings["telegram"]["bot_token"]
TELEGRAM_CHAT_ID = settings["telegram"]["chat_id"]

def send_telegram_alert(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        if not response.ok:
            print("❌ Telegram alert failed:", response.text)
    except Exception as e:
        print("❌ Error sending Telegram alert:", str(e))
