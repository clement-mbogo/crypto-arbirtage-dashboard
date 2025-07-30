import React, { useState, useEffect } from "react";
import { getSettings, toggleBacktest } from "../lib/apiClient";
import Link from "next/link";

export default function BacktestToggle() {
  const [backtestMode, setBacktestMode] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchBacktest() {
      const data = await getSettings();
      setBacktestMode(data.backtest_mode || false);
      setLoading(false);
    }
    fetchBacktest();
  }, []);

  const handleToggle = async () => {
    setLoading(true);
    const data = await toggleBacktest();
    setBacktestMode(data.backtest_mode);
    setLoading(false);
  };

  return (
    <div className="p-6 max-w-md mx-auto bg-white rounded shadow mt-8">
      <h2 className="text-xl font-semibold mb-4">Backtest Mode</h2>
      {loading ? (
        <p>Loading...</p>
      ) : (
        <>
          <p className="mb-4">
            Current Mode:{" "}
            <span className={backtestMode ? "text-green-600" : "text-red-600"}>
              {backtestMode ? "Enabled" : "Disabled"}
            </span>
          </p>
          <button
            onClick={handleToggle}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            {backtestMode ? "Disable" : "Enable"} Backtest Mode
          </button>
        </>
      )}
      <Link href="/">
        <a className="mt-6 inline-block text-blue-500 underline">Back to Home</a>
      </Link>
    </div>
  );
}
