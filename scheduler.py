import time
import threading
from arbitrage import run_arbitrage
from backtest_control import is_backtest_enabled
from database import store_performance_data
from binance_utils import get_current_prices

def schedule_task(interval=30):
    def task():
        while True:
            try:
                if not is_backtest_enabled():
                    prices = get_current_prices()
                    run_arbitrage(prices)
                    store_performance_data()
                    print("[Scheduler] Arbitrage executed and data stored.")
                else:
                    print("[Scheduler] Backtest mode enabled – skipping live trade.")
            except Exception as e:
                print(f"[Scheduler] Error: {e}")
            time.sleep(interval)

    thread = threading.Thread(target=task, daemon=True)
    thread.start()
