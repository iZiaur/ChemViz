import React, { useState, useMemo } from 'react';

const TYPE_COLORS = {
  'Pump':              { bg: 'rgba(0,200,160,.12)',   text: '#00c8a0' },
  'Heat Exchanger':    { bg: 'rgba(59,130,246,.12)',  text: '#3b82f6' },
  'Column':            { bg: 'rgba(167,139,250,.12)', text: '#a78bfa' },
  'Reactor':           { bg: 'rgba(245,158,11,.12)',  text: '#f59e0b' },
  'Separator':         { bg: 'rgba(239,68,68,.12)',   text: '#ef4444' },
  'Dryer':             { bg: 'rgba(6,182,212,.12)',   text: '#06b6d4' },
  'Valve':             { bg: 'rgba(16,185,129,.12)',  text: '#10b981' },
  'Pressure Vessel':   { bg: 'rgba(236,72,153,.12)',  text: '#ec4899' },
  'Storage Tank':      { bg: 'rgba(249,115,22,.12)',  text: '#f97316' },
  'Cooling Tower':     { bg: 'rgba(139,92,246,.12)',  text: '#8b5cf6' },
  'Compressor':        { bg: 'rgba(20,184,166,.12)',  text: '#14b8a6' },
};

const getTypeStyle = (type) => TYPE_COLORS[type] || { bg: 'rgba(255,255,255,.08)', text: '#8a9bb0' };

const columns = [
  { key: 'equipment_name', label: 'Equipment Name', align: 'left' },
  { key: 'equipment_type', label: 'Type', align: 'left' },
  { key: 'flowrate',       label: 'Flowrate (L/min)', align: 'right' },
  { key: 'pressure',       label: 'Pressure (bar)', align: 'right' },
  { key: 'temperature',    label: 'Temp (°C)', align: 'right' },
];

const DataTable = ({ records }) => {
  const [sortKey, setSortKey] = useState('equipment_name');
  const [sortDir, setSortDir] = useState(1); // 1 asc, -1 desc

  const sorted = useMemo(() => {
    if (!records) return [];
    return [...records].sort((a, b) => {
      const va = a[sortKey], vb = b[sortKey];
      if (typeof va === 'string') return sortDir * va.localeCompare(vb);
      return sortDir * (va - vb);
    });
  }, [records, sortKey, sortDir]);

  const handleSort = (key) => {
    if (sortKey === key) setSortDir(-sortDir);
    else { setSortKey(key); setSortDir(1); }
  };

  if (!records || records.length === 0) return null;

  return (
    <div className="card" style={styles.tableCard}>
      <h3 style={styles.tableTitle}>
        Equipment Records
        <span style={styles.recordCount}>{records.length} items</span>
      </h3>
      <div style={styles.scrollWrapper}>
        <table style={styles.table}>
          <thead>
            <tr>
              <th style={{ ...styles.th, width: 40 }}>#</th>
              {columns.map(col => (
                <th
                  key={col.key}
                  style={{ ...styles.th, textAlign: col.align, cursor: 'pointer' }}
                  onClick={() => handleSort(col.key)}
                >
                  {col.label}
                  {sortKey === col.key && (
                    <span style={styles.sortArrow}>{sortDir === 1 ? ' ↑' : ' ↓'}</span>
                  )}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {sorted.map((rec, i) => {
              const tc = getTypeStyle(rec.equipment_type);
              return (
                <tr key={rec.id || i} style={styles.row}>
                  <td style={{ ...styles.td, color: '#5a6a7d', fontSize: '.78rem' }}>{i + 1}</td>
                  <td style={{ ...styles.td, textAlign: 'left' }}>{rec.equipment_name}</td>
                  <td style={{ ...styles.td, textAlign: 'left' }}>
                    <span style={{ ...styles.badge, background: tc.bg, color: tc.text }}>
                      {rec.equipment_type}
                    </span>
                  </td>
                  <td style={{ ...styles.td, textAlign: 'right', fontFamily: 'JetBrains Mono, monospace', fontSize: '.82rem' }}>
                    {rec.flowrate.toFixed(1)}
                  </td>
                  <td style={{ ...styles.td, textAlign: 'right', fontFamily: 'JetBrains Mono, monospace', fontSize: '.82rem' }}>
                    {rec.pressure.toFixed(1)}
                  </td>
                  <td style={{ ...styles.td, textAlign: 'right', fontFamily: 'JetBrains Mono, monospace', fontSize: '.82rem' }}>
                    {rec.temperature.toFixed(1)}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};

const styles = {
  tableCard: { padding: '18px 0 0', overflow: 'hidden' },
  tableTitle: {
    padding: '0 18px',
    color: '#e8ecf0',
    fontSize: '.95rem',
    fontWeight: 600,
    marginBottom: 14,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  recordCount: {
    background: 'rgba(0,200,160,.12)',
    color: '#00c8a0',
    fontSize: '.72rem',
    padding: '2px 8px',
    borderRadius: 12,
    fontWeight: 500,
  },
  scrollWrapper: { overflowX: 'auto' },
  table: {
    width: '100%',
    borderCollapse: 'collapse',
    tableLayout: 'fixed',
    minWidth: 600,
  },
  th: {
    padding: '10px 14px',
    background: 'rgba(255,255,255,.03)',
    color: '#5a6a7d',
    fontSize: '.72rem',
    fontWeight: 600,
    textTransform: 'uppercase',
    letterSpacing: '0.06em',
    borderBottom: '1px solid rgba(255,255,255,.07)',
    whiteSpace: 'nowrap',
    userSelect: 'none',
  },
  sortArrow: { color: '#00c8a0' },
  row: {
    borderBottom: '1px solid rgba(255,255,255,.04)',
    transition: 'background .15s',
  },
  td: {
    padding: '9px 14px',
    color: '#c8d4e0',
    fontSize: '.84rem',
  },
  badge: {
    display: 'inline-block',
    padding: '2px 8px',
    borderRadius: 14,
    fontSize: '.72rem',
    fontWeight: 500,
  },
};

export default DataTable;
