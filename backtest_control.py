import json
import os

SETTINGS_FILE = "settings.json"

# Load current settings
def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return {"backtest": False}
    
    with open(SETTINGS_FILE, "r") as f:
        return json.load(f)

# Save updated settings
def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)

# Enable or disable backtest mode
def toggle_backtest():
    settings = load_settings()
    settings["backtest"] = not settings.get("backtest", False)
    save_settings(settings)
    return settings["backtest"]

# Check if backtest mode is enabled
def is_backtest_enabled():
    settings = load_settings()
    return settings.get("backtest", False)
