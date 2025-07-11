# core/arbitrage.py

import time
from utils.metrics import calculate_roi
from risk.filters import should_trade

class ArbitrageEngine:
    def __init__(self, exchanges, settings):
        self.exchanges = exchanges
        self.settings = settings

    def scan_opportunities(self):
        pairs = self.settings['PAIRS']
        min_diff = self.settings['MIN_PROFIT_DIFF']

        for pair in pairs:
            prices = {}
            for ex in self.exchanges:
                prices[ex.name] = ex.get_price(pair)

            sorted_prices = sorted(prices.items(), key=lambda x: x[1])
            buy_exchange, buy_price = sorted_prices[0]
            sell_exchange, sell_price = sorted_prices[-1]
            diff = ((sell_price - buy_price) / buy_price) * 100

            if diff >= min_diff:
                if should_trade(pair, diff):
                    amount = self.settings['TRADE_AMOUNT']
                    print(f"[TRADE] Buy {pair} on {buy_exchange} @ {buy_price}, Sell on {sell_exchange} @ {sell_price} | Diff: {diff:.2f}%")

                    buy_ex = next(ex for ex in self.exchanges if ex.name == buy_exchange)
                    sell_ex = next(ex for ex in self.exchanges if ex.name == sell_exchange)

                    buy_ex.buy(pair, amount)
                    sell_ex.sell(pair, amount)

                    roi = calculate_roi(buy_price, sell_price, amount)
                    print(f"[RESULT] ROI: {roi:.3f}%")
                else:
                    print(f"[SKIP] Risk filter blocked trade for {pair} ({diff:.2f}%)")
            else:
                print(f"[NO ARB] {pair} spread too low: {diff:.2f}%")
