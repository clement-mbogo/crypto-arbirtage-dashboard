openapi_schema = {
    "openapi": "3.0.0",
    "info": {
        "title": "Crypto Arbitrage Dashboard API",
        "version": "1.0.0",
        "description": "API for tracking arbitrage trades and performance"
    },
    "paths": {
        "/api/health": {
            "get": {
                "summary": "Health Check",
                "description": "Returns a simple status message.",
                "responses": {
                    "200": {
                        "description": "Successful health check",
                        "content": {
                            "application/json": {
                                "example": {
                                    "status": "ok"
                                }
                            }
                        }
                    }
                }
            }
        },
        "/api/trades": {
            "get": {
                "summary": "Get Recent Trades",
                "description": "Returns the latest 100 arbitrage trades.",
                "responses": {
                    "200": {
                        "description": "List of trades",
                        "content": {
                            "application/json": {
                                "example": [
                                    {
                                        "id": 1,
                                        "timestamp": "2025-07-25T10:15:00",
                                        "symbol": "BTC/USDT",
                                        "buy_exchange": "Binance",
                                        "sell_exchange": "Kraken",
                                        "buy_price": 29200.5,
                                        "sell_price": 29350.2,
                                        "profit_percent": 0.52,
                                        "volume": 0.01,
                                        "trade_type": "live"
                                    }
                                ]
                            }
                        }
                    }
                }
            }
        }
    }
}
