import React from 'react';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, LineElement, PointElement, Title, Filler } from 'chart.js';
import { Doughnut, Bar, Line } from 'react-chartjs-2';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, LineElement, PointElement, Title, Filler);

/* ──── Shared helpers ──── */
const PALETTE = ['#00c8a0','#3b82f6','#f59e0b','#a78bfa','#ef4444','#06b6d4','#ec4899','#10b981','#8b5cf6','#f97316'];

const tooltipPlugin = {
  backgroundColor: '#1c2636',
  titleColor: '#e8ecf0',
  bodyColor: '#8a9bb0',
  borderColor: 'rgba(255,255,255,.1)',
  borderWidth: 1,
  cornerRadius: 8,
  titleFont: { family: 'Inter', size: 12, weight: '600' },
  bodyFont:  { family: 'Inter', size: 11 },
  padding: 10,
  displayColors: true,
  boxPadding: 4,
};

const legendPlugin = {
  labels: {
    color: '#8a9bb0',
    font: { family: 'Inter', size: 11 },
    boxWidth: 10,
    boxHeight: 10,
    borderRadius: 3,
    padding: 14,
  },
};

/* ──── 1. Doughnut – Type Distribution ──── */
export const TypeDistributionChart = ({ distribution }) => {
  if (!distribution || Object.keys(distribution).length === 0) return null;

  const labels = Object.keys(distribution);
  const data = Object.values(distribution);

  return (
    <div className="card" style={styles.chartCard}>
      <h3 style={styles.chartTitle}>Type Distribution</h3>
      <Doughnut
        data={{
          labels,
          datasets: [{
            data,
            backgroundColor: labels.map((_, i) => PALETTE[i % PALETTE.length]),
            borderColor: '#161e2a',
            borderWidth: 3,
            hoverBorderWidth: 4,
          }],
        }}
        options={{
          responsive: true,
          maintainAspectRatio: true,
          cutout: '62%',
          plugins: { tooltip: tooltipPlugin, legend: { ...legendPlugin, position: 'bottom' } },
        }}
        style={{ maxHeight: 280 }}
      />
    </div>
  );
};

/* ──── 2. Bar – Average Metrics by Type ──── */
export const MetricsByTypeChart = ({ records }) => {
  if (!records || records.length === 0) return null;

  // Group by type
  const grouped = {};
  records.forEach((r) => {
    if (!grouped[r.equipment_type]) grouped[r.equipment_type] = { flowrate: [], pressure: [], temperature: [] };
    grouped[r.equipment_type].flowrate.push(r.flowrate);
    grouped[r.equipment_type].pressure.push(r.pressure);
    grouped[r.equipment_type].temperature.push(r.temperature);
  });

  const labels = Object.keys(grouped);
  const avg = (arr) => arr.reduce((a, b) => a + b, 0) / arr.length;

  return (
    <div className="card" style={styles.chartCard}>
      <h3 style={styles.chartTitle}>Avg Metrics by Equipment Type</h3>
      <Bar
        data={{
          labels,
          datasets: [
            { label: 'Flowrate (L/min)', data: labels.map(l => +avg(grouped[l].flowrate).toFixed(2)), backgroundColor: '#3b82f6', borderRadius: 4, borderSkipped: false },
            { label: 'Pressure (bar)',   data: labels.map(l => +avg(grouped[l].pressure).toFixed(2)),   backgroundColor: '#f59e0b', borderRadius: 4, borderSkipped: false },
            { label: 'Temp (°C)',        data: labels.map(l => +avg(grouped[l].temperature).toFixed(2)),backgroundColor: '#ef4444', borderRadius: 4, borderSkipped: false },
          ],
        }}
        options={{
          responsive: true,
          maintainAspectRatio: true,
          plugins: { tooltip: tooltipPlugin, legend: legendPlugin },
          scales: {
            x: {
              ticks: { color: '#8a9bb0', font: { size: 10, family: 'Inter' }, maxRotation: 35 },
              grid: { color: 'rgba(255,255,255,.04)' },
            },
            y: {
              ticks: { color: '#8a9bb0', font: { size: 10, family: 'Inter' } },
              grid: { color: 'rgba(255,255,255,.06)' },
              beginAtZero: true,
            },
          },
        }}
        style={{ maxHeight: 300 }}
      />
    </div>
  );
};

/* ──── 3. Line – All Records Trend ──── */
export const TrendChart = ({ records }) => {
  if (!records || records.length === 0) return null;

  const labels = records.map((r, i) => r.equipment_name.length > 16 ? r.equipment_name.slice(0, 14) + '…' : r.equipment_name);

  return (
    <div className="card" style={styles.chartCard}>
      <h3 style={styles.chartTitle}>Parameter Trend Across Equipment</h3>
      <Line
        data={{
          labels,
          datasets: [
            {
              label: 'Flowrate (L/min)',
              data: records.map(r => r.flowrate),
              borderColor: '#3b82f6',
              backgroundColor: 'rgba(59,130,246,.08)',
              borderWidth: 2,
              pointBackgroundColor: '#3b82f6',
              pointRadius: 3,
              pointHoverRadius: 5,
              tension: 0.3,
              fill: true,
            },
            {
              label: 'Pressure (bar)',
              data: records.map(r => r.pressure),
              borderColor: '#f59e0b',
              backgroundColor: 'rgba(245,158,11,.06)',
              borderWidth: 2,
              pointBackgroundColor: '#f59e0b',
              pointRadius: 3,
              pointHoverRadius: 5,
              tension: 0.3,
              fill: true,
            },
            {
              label: 'Temp (°C)',
              data: records.map(r => r.temperature),
              borderColor: '#ef4444',
              backgroundColor: 'rgba(239,68,68,.06)',
              borderWidth: 2,
              pointBackgroundColor: '#ef4444',
              pointRadius: 3,
              pointHoverRadius: 5,
              tension: 0.3,
              fill: true,
            },
          ],
        }}
        options={{
          responsive: true,
          maintainAspectRatio: true,
          interaction: { mode: 'index', intersect: false },
          plugins: { tooltip: tooltipPlugin, legend: legendPlugin },
          scales: {
            x: {
              ticks: { color: '#8a9bb0', font: { size: 9, family: 'Inter' }, maxRotation: 45 },
              grid: { color: 'rgba(255,255,255,.03)' },
            },
            y: {
              ticks: { color: '#8a9bb0', font: { size: 10, family: 'Inter' } },
              grid: { color: 'rgba(255,255,255,.06)' },
              beginAtZero: true,
            },
          },
        }}
        style={{ maxHeight: 300 }}
      />
    </div>
  );
};

const styles = {
  chartCard: {
    padding: '20px 18px 12px',
  },
  chartTitle: {
    color: '#e8ecf0',
    fontSize: '.95rem',
    fontWeight: 600,
    marginBottom: 14,
    display: 'flex',
    alignItems: 'center',
    gap: 8,
  },
};
