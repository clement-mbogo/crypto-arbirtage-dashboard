import React, { useEffect, useState } from "react";
import { getBalance } from "../lib/apiClient";
import Link from "next/link";

export default function Balance() {
  const [balance, setBalance] = useState(null);

  useEffect(() => {
    async function fetchBalance() {
      const data = await getBalance();
      setBalance(data);
    }
    fetchBalance();
  }, []);

  return (
    <div className="p-6 max-w-md mx-auto bg-white rounded shadow mt-8">
      <h2 className="text-xl font-semibold mb-4">Binance Balance</h2>
      {!balance ? (
        <p>Loading...</p>
      ) : (
        <ul>
          {Object.entries(balance).map(([asset, amount]) => (
            <li key={asset}>
              <strong>{asset}:</strong> {amount}
            </li>
          ))}
        </ul>
      )}
      <Link href="/">
        <a className="mt-6 inline-block text-blue-500 underline">Back to Home</a>
      </Link>
    </div>
  );
}
