# notifier.py

import os
import json
import logging
import requests

# Load bot credentials from environment or settings.json
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")
CONFIG_FILE = "settings.json"

def _load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def send_telegram_message(message: str):
    """
    Send a message via Telegram Bot API.
    Falls back to settings.json if env vars are missing.
    """
    global TG_BOT_TOKEN, TG_CHAT_ID

    if not TG_BOT_TOKEN or not TG_CHAT_ID:
        cfg = _load_config()
        TG_BOT_TOKEN = TG_BOT_TOKEN or cfg.get("TG_BOT_TOKEN")
        TG_CHAT_ID = TG_CHAT_ID or cfg.get("TG_CHAT_ID")

    if not TG_BOT_TOKEN or not TG_CHAT_ID:
        logging.warning("Telegram credentials not set; cannot send message.")
        return

    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TG_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        logging.info("Telegram message sent.")
    except Exception as e:
        logging.error(f"Failed to send Telegram message: {e}")
