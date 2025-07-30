import { useEffect, useState } from 'react';
import axios from 'axios';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement
} from 'chart.js';

ChartJS.register(LineElement, CategoryScale, LinearScale, PointElement);

const API_URL = process.env.NEXT_PUBLIC_API_URL!;

export default function Home() {
  const [balance, setBalance] = useState<Record<string, any> | null>(null);
  const [performance, setPerformance] = useState<any[]>([]);
  const [trades, setTrades] = useState<any[]>([]);
  const [backtestMode, setBacktestMode] = useState(false);
  const [formData, setFormData] = useState({ symbol: '', side: 'BUY', qty: 0 });

  useEffect(() => {
    fetchBalance();
    fetchPerformance();
    fetchTrades();
    fetchBacktestMode();
  }, []);

  const fetchBalance = async () => {
    try {
      const res = await axios.get(`${API_URL}/balance`);
      setBalance(res.data);
    } catch (error) {
      console.error("Fetch balance error:", error);
    }
  };

  const fetchPerformance = async () => {
    try {
      const res = await axios.get(`${API_URL}/performance`);
      setPerformance(res.data);
    } catch (error) {
      console.error("Fetch performance error:", error);
    }
  };

  const fetchTrades = async () => {
    try {
      const res = await axios.get(`${API_URL}/trades`);
      setTrades(res.data);
    } catch (error) {
      console.error("Fetch trades error:", error);
    }
  };

  const fetchBacktestMode = async () => {
    try {
      const res = await axios.get(`${API_URL}/backtest`);
      setBacktestMode(res.data.backtest_mode);
    } catch (error) {
      console.error("Fetch backtest mode error:", error);
    }
  };

  const toggleBacktest = async () => {
    try {
      const res = await axios.post(`${API_URL}/backtest`);
      setBacktestMode(res.data.backtest_mode);
    } catch (error) {
      console.error("Toggle backtest error:", error);
    }
  };

  const executeTrade = async () => {
    try {
      await axios.post(`${API_URL}/execute_trade`, formData);
      alert('Trade executed');
    } catch (error) {
      console.error("Execute trade error:", error);
      alert('Failed to execute trade');
    }
  };

  const chartData = {
    labels: performance.map(p => p.timestamp),
    datasets: [
      {
        label: 'Capital',
        data: performance.map(p => p.capital),
        fill: false,
        borderColor: 'blue',
        tension: 0.1,
      },
    ],
  };

  return (
    <div className="p-4 max-w-4xl mx-auto space-y-6">
      <h1 className="text-3xl font-bold text-center">Crypto Arbitrage Dashboard</h1>

      <section className="bg-gray-100 p-4 rounded shadow">
        <h2 className="text-xl font-semibold">Balance</h2>
        {balance ? (
          <ul>
            {Object.entries(balance).map(([key, value]) => (
              <li key={key}>{key}: {value}</li>
            ))}
          </ul>
        ) : (
          'Loading...'
        )}
      </section>

      <section className="bg-gray-100 p-4 rounded shadow">
        <h2 className="text-xl font-semibold">Performance Chart</h2>
        <Line data={chartData} />
      </section>

      <section className="bg-gray-100 p-4 rounded shadow">
        <h2 className="text-xl font-semibold">Trade History</h2>
        <ul>
          {trades.map((t, i) => (
            <li key={i}>{t.timestamp} - {t.symbol} - {t.side} - {t.price} @ {t.qty}</li>
          ))}
        </ul>
      </section>

      <section className="bg-gray-100 p-4 rounded shadow">
        <h2 className="text-xl font-semibold">Backtest Mode</h2>
        <p>Current: {backtestMode ? 'Enabled' : 'Disabled'}</p>
        <button
          onClick={toggleBacktest}
          className="bg-blue-500 text-white px-4 py-2 rounded mt-2"
        >
          Toggle Backtest
        </button>
      </section>

      <section className="bg-gray-100 p-4 rounded shadow">
        <h2 className="text-xl font-semibold">Execute Trade</h2>
        <input
          type="text"
          placeholder="Symbol (e.g. BTCUSDT)"
          className="border p-2 mr-2"
          onChange={e => setFormData({ ...formData, symbol: e.target.value })}
        />
        <select
          className="border p-2 mr-2"
          onChange={e => setFormData({ ...formData, side: e.target.value })}
          value={formData.side}
        >
          <option value="BUY">BUY</option>
          <option value="SELL">SELL</option>
        </select>
        <input
          type="number"
          placeholder="Qty"
          className="border p-2 mr-2"
          onChange={e => setFormData({ ...formData, qty: parseFloat(e.target.value) || 0 })}
        />
        <button
          onClick={executeTrade}
          className="bg-green-600 text-white px-4 py-2 rounded"
        >
          Execute
        </button>
      </section>
    </div>
  );
}
