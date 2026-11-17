import { getDashboard } from "./api.js";

const colors = {
  Positive: "#087b4b",
  Neutral: "#d99213",
  Negative: "#d7252b",
};

let distributionChart;
let activityChart;

function formatTime(value) {
  if (!value) return "—";
  const parsed = new Date(value.replace(" ", "T"));
  return Number.isNaN(parsed.getTime())
    ? value
    : new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short" }).format(parsed);
}

function makeCell(row, value, className) {
  const cell = document.createElement("td");
  if (className) cell.className = className;
  cell.textContent = value ?? "";
  row.append(cell);
  return cell;
}

function sentimentBadge(value) {
  const badge = document.createElement("span");
  badge.className = `sentiment-badge ${(value || "").toLowerCase()}`;
  badge.textContent = value || "Unknown";
  return badge;
}

function renderRecent(records) {
  const body = document.querySelector("#recent-rows");
  body.replaceChildren();

  if (!records?.length) {
    const row = document.createElement("tr");
    const cell = makeCell(row, "No saved analyses yet.", "table-message");
    cell.colSpan = 5;
    body.append(row);
    document.querySelector("#recent-count").textContent = "0 records";
    return;
  }

  for (const record of records) {
    const row = document.createElement("tr");
    const source = makeCell(row, "", "");
    const sourceTag = document.createElement("span");
    sourceTag.className = "source-tag";
    sourceTag.textContent = record.source || "Unknown";
    source.append(sourceTag);
    if (record.is_demo) {
      const demoTag = document.createElement("span");
      demoTag.className = "demo-tag";
      demoTag.textContent = "DEMO";
      source.append(demoTag);
    }

    const reviewText = (record.text || "").split("Review: ").pop().replace(/\s+/g, " ");
    const snippet = record.customer_name
      ? `${record.customer_name} · ${record.product_name || "Customer review"} · ${reviewText}`
      : (record.text || "").replace(/\s+/g, " ");
    const textCell = makeCell(row, snippet, "");
    textCell.title = snippet;
    textCell.classList.add("snippet-cell");
    const sentimentCell = makeCell(row, "", "");
    sentimentCell.append(sentimentBadge(record.sentiment));
    makeCell(row, `${Number(record.confidence || 0).toFixed(1)}%`, "confidence-cell");
    makeCell(row, formatTime(record.time), "");
    body.append(row);
  }
  document.querySelector("#recent-count").textContent = `${records.length} latest records`;
}

function updateCharts(data) {
  if (typeof Chart === "undefined") {
    throw new Error("Chart.js did not load. Check your internet connection and refresh.");
  }

  const distributionContext = document.querySelector("#distribution-chart");
  const activityContext = document.querySelector("#activity-chart");
  distributionChart?.destroy();
  activityChart?.destroy();

  const labels = ["Positive", "Neutral", "Negative"];
  const values = labels.map((label) => data.distribution?.[label]?.count || 0);
  distributionChart = new Chart(distributionContext, {
    type: "doughnut",
    data: {
      labels,
      datasets: [{
        data: values,
        backgroundColor: labels.map((label) => colors[label]),
        borderColor: "#fff",
        borderWidth: 3,
        hoverOffset: 5,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: "67%",
      plugins: {
        legend: {
          position: "bottom",
          labels: { usePointStyle: true, pointStyle: "circle", boxWidth: 7, padding: 14, font: { size: 11 } },
        },
        tooltip: { callbacks: { label: (context) => `${context.label}: ${context.raw} analyses` } },
      },
    },
  });

  const activity = data.activity || [];
  activityChart = new Chart(activityContext, {
    type: "line",
    data: {
      labels: activity.map((item) => item.date),
      datasets: labels.map((label) => ({
        label,
        data: activity.map((item) => item[label] || 0),
        borderColor: colors[label],
        backgroundColor: colors[label],
        borderWidth: 2,
        pointRadius: 3,
        pointHoverRadius: 5,
        tension: 0.3,
      })),
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: "index", intersect: false },
      plugins: {
        legend: {
          position: "top",
          align: "end",
          labels: { usePointStyle: true, pointStyle: "circle", boxWidth: 7, padding: 12, font: { size: 10 } },
        },
      },
      scales: {
        x: { grid: { display: false }, ticks: { maxRotation: 0, autoSkip: true, maxTicksLimit: 6, font: { size: 10 } } },
        y: { beginAtZero: true, ticks: { precision: 0, font: { size: 10 } }, grid: { color: "#edf0f8" } },
      },
    },
  });
}

export async function refreshDashboard() {
  const status = document.querySelector("#dashboard-status");
  status.textContent = "Loading dashboard data…";
  const days = document.querySelector("#dashboard-range").value;
  try {
    const data = await getDashboard(days ? { days } : {});
    document.querySelector('[data-metric="total"]').textContent = Number(data.total_analyses).toLocaleString();
    for (const label of ["Positive", "Neutral", "Negative"]) {
      const key = label.toLowerCase();
      const classData = data.distribution[label];
      document.querySelector(`[data-metric="${key}"]`).textContent = Number(classData.count).toLocaleString();
      document.querySelector(`[data-share="${key}"]`).textContent = `${Number(classData.percentage).toFixed(1)}% of saved records`;
    }

    document.querySelector("#model-accuracy").textContent = `${Number(data.model_evaluation.accuracy).toFixed(2)}%`;
    document.querySelector("#model-f1").textContent = Number(data.model_evaluation.macro_f1).toFixed(3);
    document.querySelector("#model-dataset").textContent = data.model_evaluation.dataset;
    const demoNotice = document.querySelector("#dashboard-demo-notice");
    const demoCount = Number(data.demo_records_count || 0);
    demoNotice.hidden = demoCount === 0;
    demoNotice.textContent = demoCount
      ? `${demoCount} fictional customer reviews or comments are included in these statistics and clearly labeled as demo data.`
      : "";
    renderRecent(data.recent_analyses);
    updateCharts(data);
    status.textContent = "";
  } catch (error) {
    status.textContent = error.message;
  }
}

export function initDashboard() {
  document.querySelector("#dashboard-refresh").addEventListener("click", refreshDashboard);
  document.querySelector("#dashboard-range").addEventListener("change", refreshDashboard);
}
