# telegram_alerts.py

import json
import requests

TG_BOT_TOKEN = "your_telegram_bot_token"
TG_CHAT_ID = "your_telegram_chat_id"
ALERTS_FILE = "settings/alerts.json"

def is_alerts_enabled():
    try:
        with open(ALERTS_FILE, "r") as f:
            data = json.load(f)
        return data.get("enabled", False)
    except Exception:
        return False

def send_telegram_alert(message):
    if not is_alerts_enabled():
        return

    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TG_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Telegram alert failed: {e}")
