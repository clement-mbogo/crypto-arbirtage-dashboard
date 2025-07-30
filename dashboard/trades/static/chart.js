<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
let chart;
let chartType = "capital";
let isLiveMode = false;

// Load mode from toggle button if you have one
function getMode() {
  // This depends on your toggle setup. For now it's hardcoded.
  return isLiveMode ? 'live' : 'paper';
}

function fetchChartData() {
  fetch(`/get_chart_data?mode=${getMode()}&type=${chartType}`)
    .then(response => response.json())
    .then(data => {
      updateChart(data);
    });
}

function updateChart(data) {
  const labels = data.timestamps.map(ts => new Date(ts * 1000).toLocaleTimeString());
  const dataset = data.values;

  if (chart) {
    chart.data.labels = labels;
    chart.data.datasets[0].data = dataset;
    chart.data.datasets[0].label = chartType.replace('_', ' ').toUpperCase();
    chart.update();
  } else {
    const ctx = document.getElementById("growthChart").getContext("2d");
    chart = new Chart(ctx, {
      type: "line",
      data: {
        labels: labels,
        datasets: [{
          label: chartType.replace('_', ' ').toUpperCase(),
          data: dataset,
          fill: true,
          borderColor: "#4bc0c0",
          backgroundColor: "rgba(75, 192, 192, 0.2)",
          tension: 0.2
        }]
      },
      options: {
        responsive: true,
        scales: {
          x: { display: true },
          y: { display: true }
        }
      }
    });
  }
}

document.getElementById("chartType").addEventListener("change", function () {
  chartType = this.value;
  fetchChartData();
});

// Initial load
fetchChartData();
setInterval(fetchChartData, 15000); // refresh every 15s
</script>
