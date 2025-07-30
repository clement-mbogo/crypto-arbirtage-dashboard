import React, { useState } from "react";
import { executeTrade } from "../lib/apiClient";
import Link from "next/link";

export default function ExecuteTrade() {
  const [symbol, setSymbol] = useState("");
  const [side, setSide] = useState("BUY");
  const [qty, setQty] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const submitTrade = async () => {
    if (!symbol || !qty) {
      alert("Please enter symbol and quantity.");
      return;
    }
    setLoading(true);
    const data = await executeTrade(symbol.toUpperCase(), side, parseFloat(qty));
    setResult(data);
    setLoading(false);
  };

  return (
    <div className="p-6 max-w-md mx-auto bg-white rounded shadow mt-8">
      <h2 className="text-xl font-semibold mb-4">Execute Trade</h2>
      <input
        className="w-full p-2 border mb-2 rounded"
        placeholder="Symbol (e.g. BTCUSDT)"
        value={symbol}
        onChange={(e) => setSymbol(e.target.value)}
      />
      <select
        className="w-full p-2 border mb-2 rounded"
        value={side}
        onChange={(e) => setSide(e.target.value)}
      >
        <option value="BUY">Buy</option>
        <option value="SELL">Sell</option>
      </select>
      <input
        className="w-full p-2 border mb-4 rounded"
        placeholder="Quantity"
        type="number"
        value={qty}
        onChange={(e) => setQty(e.target.value)}
      />
      <button
        className="w-full py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        onClick={submitTrade}
        disabled={loading}
      >
        {loading ? "Executing..." : "Submit Trade"}
      </button>
      {result && (
        <pre className="mt-4 p-2 bg-gray-100 rounded max-h-48 overflow-auto text-sm">
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
      <Link href="/">
        <a className="mt-6 inline-block text-blue-500 underline">Back to Home</a>
      </Link>
    </div>
  );
}
