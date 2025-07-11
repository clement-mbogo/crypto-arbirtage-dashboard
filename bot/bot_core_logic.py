# bot/main.py

import time
from exchanges.binance import Binance
from exchanges.kucoin import KuCoin
from core.arbitrage import ArbitrageEngine
from config.settings import load_settings

settings = load_settings()

def main():
    print("[START] Crypto Arbitrage Bot Running...")
    binance = Binance(settings)
    kucoin = KuCoin(settings)

    engine = ArbitrageEngine([binance, kucoin], settings)

    while True:
        engine.scan_opportunities()
        time.sleep(settings["SCAN_INTERVAL"])

if __name__ == "__main__":
    main()
