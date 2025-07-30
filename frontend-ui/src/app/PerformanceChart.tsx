"use client";

import { useEffect, useState } from "react";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  Legend,
  Tooltip,
} from "chart.js";

ChartJS.register(LineElement, PointElement, CategoryScale, LinearScale, Legend, Tooltip);

interface DataPoint {
  timestamp: string;
  capital: number;
  profit_percent: number;
}

export default function PerformanceChart() {
  const [dataPoints, setDataPoints] = useState<DataPoint[]>([]);

  useEffect(() => {
    const fetchPerformance = async () => {
      const res = await fetch("/api/performance");
      const data = await res.json();

      const now = new Date().toLocaleTimeString();

      setDataPoints((prev) => [
        ...prev.slice(-20), // keep only latest 20 points
        {
          timestamp: now,
          capital: data.capital,
          profit_percent: data.profit_percent,
        },
      ]);
    };

    fetchPerformance();
    const interval = setInterval(fetchPerformance, 5000);
    return () => clearInterval(interval);
  }, []);

  const chartData = {
    labels: dataPoints.map((d) => d.timestamp),
    datasets: [
      {
        label: "Capital ($)",
        data: dataPoints.map((d) => d.capital),
        borderColor: "#3b82f6",
        backgroundColor: "rgba(59, 130, 246, 0.2)",
        yAxisID: "y1",
      },
      {
        label: "Profit (%)",
        data: dataPoints.map((d) => d.profit_percent),
        borderColor: "#10b981",
        backgroundColor: "rgba(16, 185, 129, 0.2)",
        yAxisID: "y2",
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    interaction: {
      mode: "index" as const,
      intersect: false,
    },
    stacked: false,
    plugins: {
      legend: {
        position: "top" as const,
      },
    },
    scales: {
      y1: {
        type: "linear" as const,
        position: "left" as const,
        title: {
          display: true,
          text: "Capital",
        },
      },
      y2: {
        type: "linear" as const,
        position: "right" as const,
        title: {
          display: true,
          text: "Profit %",
        },
        grid: {
          drawOnChartArea: false,
        },
      },
    },
  };

  return (
    <div className="bg-white p-6 rounded-2xl shadow mt-10">
      <h2 className="text-xl font-semibold text-gray-700 mb-4">Performance Over Time</h2>
      <Line data={chartData} options={chartOptions} />
    </div>
  );
}
