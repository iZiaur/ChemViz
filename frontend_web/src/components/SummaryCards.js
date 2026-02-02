import React from 'react';

const metrics = [
  {
    label: 'Total Equipment',
    key: 'total_records',
    unit: '',
    color: '#00c8a0',
    dim: 'rgba(0,200,160,.12)',
    icon: '⛓',
  },
  {
    label: 'Avg Flowrate',
    key: 'avg_flowrate',
    unit: 'L/min',
    color: '#3b82f6',
    dim: 'rgba(59,130,246,.12)',
    icon: '◈',
  },
  {
    label: 'Avg Pressure',
    key: 'avg_pressure',
    unit: 'bar',
    color: '#f59e0b',
    dim: 'rgba(245,158,11,.12)',
    icon: '▲',
  },
  {
    label: 'Avg Temperature',
    key: 'avg_temperature',
    unit: '°C',
    color: '#ef4444',
    dim: 'rgba(239,68,68,.12)',
    icon: '◉',
  },
];

const SummaryCards = ({ summary }) => {
  if (!summary) return null;
  return (
    <div style={styles.grid}>
      {metrics.map((m) => (
        <div key={m.key} className="card" style={styles.card}>
          <div style={styles.topRow}>
            <span style={{ ...styles.icon, background: m.dim, color: m.color }}>{m.icon}</span>
            <span style={styles.label}>{m.label}</span>
          </div>
          <div style={styles.valueRow}>
            <span style={{ ...styles.value, color: m.color }}>
              {typeof summary[m.key] === 'number' && m.key !== 'total_records'
                ? summary[m.key].toFixed(2)
                : summary[m.key]}
            </span>
            {m.unit && <span style={styles.unit}>{m.unit}</span>}
          </div>
        </div>
      ))}
    </div>
  );
};

const styles = {
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: 16,
  },
  card: {
    padding: '16px 18px',
    display: 'flex',
    flexDirection: 'column',
    gap: 10,
    transition: 'transform .15s',
  },
  topRow: {
    display: 'flex',
    alignItems: 'center',
    gap: 10,
  },
  icon: {
    width: 34,
    height: 34,
    borderRadius: 8,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '1rem',
  },
  label: {
    color: '#8a9bb0',
    fontSize: '.78rem',
    fontWeight: 500,
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
  },
  valueRow: {
    display: 'flex',
    alignItems: 'baseline',
    gap: 6,
  },
  value: {
    fontSize: '1.7rem',
    fontWeight: 700,
    letterSpacing: '-0.03em',
    fontFamily: 'JetBrains Mono, monospace',
  },
  unit: {
    color: '#5a6a7d',
    fontSize: '.78rem',
    fontWeight: 400,
  },
};

export default SummaryCards;
