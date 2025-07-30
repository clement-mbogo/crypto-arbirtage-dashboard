import React, { useEffect, useState } from "react";
import { getTrades } from "../lib/apiClient";
import Link from "next/link";

export default function Trades() {
  const [trades, setTrades] = useState(null);

  useEffect(() => {
    async function fetchTrades() {
      const data = await getTrades();
      setTrades(data);
    }
    fetchTrades();
  }, []);

  return (
    <div className="p-6 max-w-4xl mx-auto bg-white rounded shadow mt-8">
      <h2 className="text-xl font-semibold mb-4">Recent Trades</h2>
      {!trades ? (
        <p>Loading...</p>
      ) : (
        <table className="min-w-full border border-gray-200">
          <thead>
            <tr className="bg-gray-100">
              <th className="border px-4 py-2">Timestamp</th>
              <th className="border px-4 py-2">Symbol</th>
              <th className="border px-4 py-2">Side</th>
              <th className="border px-4 py-2">Price</th>
              <th className="border px-4 py-2">Quantity</th>
              <th className="border px-4 py-2">Profit</th>
            </tr>
          </thead>
          <tbody>
            {trades.map((trade) => (
              <tr key={trade.id}>
                <td className="border px-4 py-2">{new Date(trade.timestamp).toLocaleString()}</td>
                <td className="border px-4 py-2">{trade.symbol}</td>
                <td className="border px-4 py-2">{trade.side}</td>
                <td className="border px-4 py-2">{trade.price}</td>
                <td className="border px-4 py-2">{trade.qty}</td>
                <td className="border px-4 py-2">{trade.profit}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      <Link href="/">
        <a className="mt-6 inline-block text-blue-500 underline">Back to Home</a>
      </Link>
    </div>
  );
}
