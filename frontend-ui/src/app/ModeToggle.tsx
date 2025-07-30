"use client";

import { useEffect, useState } from "react";

export default function ModeToggle() {
  const [backtestEnabled, setBacktestEnabled] = useState(false);
  const [loading, setLoading] = useState(false);

  const fetchBacktestStatus = async () => {
    const res = await fetch("/api/backtest_status");
    const data = await res.json();
    setBacktestEnabled(data.backtest_enabled);
  };

  useEffect(() => {
    fetchBacktestStatus();
  }, []);

  const toggleBacktest = async () => {
    setLoading(true);
    const res = await fetch("/api/toggle_backtest", { method: "POST" });
    const data = await res.json();
    setBacktestEnabled(data.backtest_enabled);
    setLoading(false);
  };

  return (
    <div className="flex items-center gap-4 bg-white p-4 rounded-xl shadow mt-6 w-fit">
      <span className="text-gray-700 font-medium">Mode:</span>
      <button
        onClick={toggleBacktest}
        className={`px-4 py-2 rounded-xl text-white transition ${
          backtestEnabled ? "bg-orange-500" : "bg-green-600"
        }`}
        disabled={loading}
      >
        {loading ? "Toggling..." : backtestEnabled ? "Backtest Mode" : "Live Mode"}
      </button>
    </div>
  );
}
