import React, { useState, useEffect, useCallback } from 'react';
import UploadZone from './UploadZone';
import SummaryCards from './SummaryCards';
import DataTable from './DataTable';
import { TypeDistributionChart, MetricsByTypeChart, TrendChart } from './Charts';
import { getHistory, getDatasetDetail } from '../services/api';

const Dashboard = () => {
  const [dataset, setDataset] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchLatest = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const histRes = await getHistory();
      const history = histRes.data;
      if (history && history.length > 0) {
        const detailRes = await getDatasetDetail(history[0].id);
        setDataset(detailRes.data);
      } else {
        setDataset(null);
      }
    } catch (err) {
      setError('Failed to load data. Please try uploading a file.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchLatest(); }, [fetchLatest]);

  return (
    <div>
      {/* Top row: upload + summary */}
      <div style={styles.topGrid}>
        <UploadZone onUploadSuccess={fetchLatest} />

        <div style={styles.rightCol}>
          {loading && <div style={styles.loadingMsg}>Loading…</div>}
          {error  && <div style={styles.errorMsg}>{error}</div>}
          {!loading && dataset && <SummaryCards summary={dataset} />}
          {!loading && !dataset && !error && (
            <div className="card" style={styles.emptyState}>
              <span style={styles.emptyIcon}>📊</span>
              <p style={styles.emptyText}>Upload a CSV file to see your dashboard.</p>
            </div>
          )}
        </div>
      </div>

      {/* Charts row */}
      {dataset && (
        <>
          <div style={{ ...styles.chartsGrid, marginTop: 24 }}>
            <TypeDistributionChart distribution={dataset.type_distribution} />
            <MetricsByTypeChart records={dataset.records} />
          </div>

          <div style={{ marginTop: 20 }}>
            <TrendChart records={dataset.records} />
          </div>

          {/* Data table */}
          <div style={{ marginTop: 20 }}>
            <DataTable records={dataset.records} />
          </div>
        </>
      )}
    </div>
  );
};

const styles = {
  topGrid: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: 20,
    alignItems: 'start',
  },
  rightCol: {
    display: 'flex',
    flexDirection: 'column',
    gap: 16,
  },
  chartsGrid: {
    display: 'grid',
    gridTemplateColumns: '1fr 1.6fr',
    gap: 20,
  },
  loadingMsg: {
    color: '#8a9bb0',
    fontSize: '.85rem',
    padding: 20,
    textAlign: 'center',
  },
  errorMsg: {
    background: 'rgba(239,68,68,.1)',
    border: '1px solid rgba(239,68,68,.25)',
    borderRadius: 8,
    padding: '10px 14px',
    color: '#ef4444',
    fontSize: '.82rem',
  },
  emptyState: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: 8,
    padding: '32px 20px',
    textAlign: 'center',
  },
  emptyIcon: { fontSize: '2rem' },
  emptyText: { color: '#5a6a7d', fontSize: '.82rem' },
};

export default Dashboard;
