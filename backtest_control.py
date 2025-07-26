import json

SETTINGS_FILE = "settings.json"

def is_backtest_enabled():
    try:
        with open(SETTINGS_FILE, "r") as f:
            settings = json.load(f)
        return settings.get("backtest", False)
    except Exception as e:
        print("❌ Could not read backtest status:", str(e))
        return False

def set_backtest_enabled(value: bool):
    try:
        with open(SETTINGS_FILE, "r") as f:
            settings = json.load(f)
        settings["backtest"] = value
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=2)
        print(f"✅ Backtest set to {value}")
    except Exception as e:
        print("❌ Failed to update backtest setting:", str(e))
