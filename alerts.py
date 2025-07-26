import requests
import json
import os

# Load Telegram bot credentials
with open("settings.json") as f:
    settings = json.load(f)

TG_BOT_TOKEN = settings.get("TG_BOT_TOKEN")
TG_CHAT_ID = settings.get("TG_CHAT_ID")

def send_telegram_alert(message):
    try:
        url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": TG_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        response = requests.post(url, data=data)
        if response.status_code != 200:
            print(f"❌ Telegram alert failed: {response.text}")
        else:
            print("✅ Telegram alert sent.")
    except Exception as e:
        print(f"❌ Error sending Telegram alert: {e}")
