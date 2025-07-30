# live_mode_control.py

import json
import os

SETTINGS_FILE = "settings.json"

def is_live_mode():
    if not os.path.exists(SETTINGS_FILE):
        return False
    with open(SETTINGS_FILE, "r") as f:
        data = json.load(f)
        return data.get("live_mode", False)

def toggle_live_mode(enabled: bool):
    data = {}
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            data = json.load(f)
    data["live_mode"] = enabled
    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f)
