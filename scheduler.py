# scheduler.py

import time
import logging
from threading import Thread
from arbitrage import run_arbitrage
from performance import save_performance
from database import get_trade_count, get_current_capital

# Time between checks (in seconds; default 5 minutes)
INTERVAL_SECONDS = 300

def calculate_profit_percent(current_capital: float, base_capital: float = 1000.0) -> float:
    """
    Calculate profit percentage relative to a base capital.
    """
    if base_capital == 0:
        return 0.0
    return ((current_capital - base_capital) / base_capital) * 100

def _scheduler_loop():
    """
    Main loop: run arbitrage checks, log performance, then sleep.
    """
    while True:
        logging.info("🔄 Scheduler tick: running arbitrage check...")
        # Run arbitrage logic (backtest or live based on settings)
        opportunities = run_arbitrage()

        # Fetch current stats
        capital = get_current_capital()
        trades_count = get_trade_count()
        profit_pct = calculate_profit_percent(capital)

        # Save performance snapshot
        save_performance(capital, profit_pct, trades_count)
        logging.info(f"📊 Performance logged: capital=${capital:.2f}, profit%={profit_pct:.2f}, trades={trades_count}")

        # Wait for next interval
        time.sleep(INTERVAL_SECONDS)

def start_scheduler():
    """
    Start the scheduler in a background daemon thread.
    """
    thread = Thread(target=_scheduler_loop, daemon=True)
    thread.start()
    logging.info("✅ Scheduler started in background thread.")
