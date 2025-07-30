import React, { useEffect, useState } from "react";
import { getPerformance } from "../lib/apiClient";
import { Line } from "react-chartjs-2";
import Link from "next/link";

import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

export default function PerformanceChart() {
  const [chartData, setChartData] = useState(null);

  useEffect(() => {
    async function fetchPerformance() {
      const data = await getPerformance();
      const chart = {
        labels: data.timestamps.map((ts) =>
          new Date(ts).toLocaleString()
        ),
        datasets: [
          {
            label: "Capital",
            data: data.capital,
            borderColor: "green",
            fill: false,
          },
          {
            label: "Profit %",
            data: data.profit_percent,
            borderColor: "blue",
            fill: false,
          },
          {
            label: "Trade Count",
            data: data.trade_count,
            borderColor: "orange",
            fill: false,
          },
        ],
      };
      setChartData(chart);
    }
    fetchPerformance();
  }, []);

  if (!chartData) return <div>Loading chart...</div>;

  return (
    <div className="p-6 max-w-3xl mx-auto bg-white rounded shadow mt-8">
      <h2 className="text-xl font-semibold mb-4">Performance Chart</h2>
      <Line data={chartData} />
      <Link href="/">
        <a className="mt-6 inline-block text-blue-500 underline">Back to Home</a>
      </Link>
    </div>
  );
}
