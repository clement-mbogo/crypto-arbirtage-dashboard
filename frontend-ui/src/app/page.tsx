"use client";

import { useEffect, useState } from "react";

export default function Home() {
  const [capital, setCapital] = useState<number | null>(null);
  const [profit, setProfit] = useState<number | null>(null);
  const [trades, setTrades] = useState<number | null>(null);
  const [backtestOn, setBacktestOn] = useState<boolean>(false);
  const [schedulerOn, setSchedulerOn] = useState<boolean>(false);

  useEffect(() => {
    const fetchData = async () => {
      const res = await fetch("/api/performance");
      const data = await res.json();
      setCapital(data.capital);
      setProfit(data.profit_percent);
      setTrades(data.total_trades);
    };

    const fetchToggles = async () => {
      const b = await fetch("/api/backtest_status");
      const s = await fetch("/api/scheduler_status");
      setBacktestOn((await b.json()).enabled);
      setSchedulerOn((await s.json()).enabled);
    };

    fetchData();
    fetchToggles();

    const interval = setInterval(() => {
      fetchData();
      fetchToggles();
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const toggleBacktest = async () => {
    await fetch("/api/toggle_backtest", { method: "POST" });
    setBacktestOn((prev) => !prev);
  };

  const toggleScheduler = async () => {
    await fetch("/api/toggle_scheduler", { method: "POST" });
    setSchedulerOn((prev) => !prev);
  };

  return (
    <main className="p-10 bg-gray-100 min-h-screen">
      <h1 className="text-3xl font-bold mb-6">Crypto Arbitrage Dashboard</h1>

      <div className="grid grid-cols-3 gap-6 mb-6">
        <div className="bg-white p-6 rounded-2xl shadow">
          <h2 className="text-lg font-semibold text-gray-700">Capital</h2>
          <p className="text-2xl text-blue-600">{capital !== null ? `$${capital.toFixed(2)}` : "Loading..."}</p>
        </div>

        <div className="bg-white p-6 rounded-2xl shadow">
          <h2 className="text-lg font-semibold text-gray-700">Profit %</h2>
          <p className="text-2xl text-green-600">{profit !== null ? `${profit.toFixed(2)}%` : "Loading..."}</p>
        </div>

        <div className="bg-white p-6 rounded-2xl shadow">
          <h2 className="text-lg font-semibold text-gray-700">Total Trades</h2>
          <p className="text-2xl text-purple-600">{trades !== null ? trades : "Loading..."}</p>
        </div>
      </div>
import PerformanceChart from "@/components/PerformanceChart";

export default function Home() {
  return (
    <main className="p-6">
      <h1 className="text-3xl font-bold mb-6">Crypto Arbitrage Dashboard</h1>
      <PerformanceChart />
    </main>
  );
}
import PerformanceChart from "@/components/PerformanceChart";
import ModeToggle from "@/components/ModeToggle";

export default function Home() {
  return (
    <main className="p-6">
      <h1 className="text-3xl font-bold mb-6">Crypto Arbitrage Dashboard</h1>
      <ModeToggle />
      <PerformanceChart />
    </main>
  );
}


      {/* Toggle Controls */}
      <div className="bg-white p-6 rounded-2xl shadow w-fit">
        <h2 className="text-xl font-semibold mb-4 text-gray-800">Simulation Controls</h2>
        <div className="flex gap-6">
          <button
            onClick={toggleBacktest}
            className={`px-6 py-2 rounded-xl font-medium ${backtestOn ? "bg-green-500 text-white" : "bg-gray-300 text-gray-800"}`}
          >
            Backtest: {backtestOn ? "ON" : "OFF"}
          </button>
          <button
            onClick={toggleScheduler}
            className={`px-6 py-2 rounded-xl font-medium ${schedulerOn ? "bg-green-500 text-white" : "bg-gray-300 text-gray-800"}`}
          >
            Scheduler: {schedulerOn ? "ON" : "OFF"}
          </button>
        </div>
      </div>
    </main>
  );
}
