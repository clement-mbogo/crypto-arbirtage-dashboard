export const API_BASE = "http://127.0.0.1:5000";

export async function getSettings() {
  const res = await fetch(`${API_BASE}/api/backtest`);
  return res.json();
}

export async function toggleBacktest() {
  const res = await fetch(`${API_BASE}/api/backtest`, { method: "POST" });
  return res.json();
}

export async function getBalance() {
  const res = await fetch(`${API_BASE}/api/balance`);
  return res.json();
}

export async function getPerformance() {
  const res = await fetch(`${API_BASE}/api/performance`);
  return res.json();
}

export async function getTrades() {
  const res = await fetch(`${API_BASE}/api/trades`);
  return res.json();
}

export async function executeTrade(symbol, side, qty) {
  const res = await fetch(`${API_BASE}/api/execute_trade`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ symbol, side, qty }),
  });
  return res.json();
}
