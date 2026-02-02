import React, { useState, useEffect, useCallback } from 'react';
import { getHistory, getDatasetDetail, deleteDataset, downloadPDF } from '../services/api';
import SummaryCards from './SummaryCards';
import DataTable from './DataTable';
import { TypeDistributionChart } from './Charts';

const History = () => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState(null);   // full dataset
  const [selectedId, setSelectedId] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [pdfLoading, setPdfLoading] = useState(null);

  const fetchHistory = useCallback(async () => {
    setLoading(true);
    try {
      const res = await getHistory();
      setHistory(res.data);
    } catch {
      setHistory([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchHistory(); }, [fetchHistory]);

  const selectDataset = async (id) => {
    setSelectedId(id);
    setDetailLoading(true);
    try {
      const res = await getDatasetDetail(id);
      setSelected(res.data);
    } catch {
      setSelected(null);
    } finally {
      setDetailLoading(false);
    }
  };

  const handleDelete = async (id, e) => {
    e.stopPropagation();
    if (!window.confirm('Delete this dataset?')) return;
    try {
      await deleteDataset(id);
      setHistory(history.filter(h => h.id !== id));
      if (selectedId === id) { setSelected(null); setSelectedId(null); }
    } catch {}
  };

  const handlePDF = async (id, e) => {
    e.stopPropagation();
    setPdfLoading(id);
    try {
      const res = await downloadPDF(id);
      const url = URL.createObjectURL(res.data);
      const a = document.createElement('a');
      a.href = url;
      a.download = `report_${id}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      alert('PDF generation failed. Check if reportlab is installed on the backend.');
    } finally {
      setPdfLoading(null);
    }
  };

  return (
    <div>
      <div style={styles.pageHeader}>
        <h2 style={styles.pageTitle}>Upload History</h2>
        <span style={styles.pageSubtitle}>Last 5 uploaded datasets</span>
      </div>

      {loading && <div style={styles.loading}>Loading…</div>}

      {!loading && history.length === 0 && (
        <div className="card" style={styles.emptyState}>
          <span style={styles.emptyIcon}>📁</span>
          <p style={styles.emptyText}>No datasets uploaded yet. Go to the Dashboard to upload your first CSV.</p>
        </div>
      )}

      {!loading && history.length > 0 && (
        <div style={styles.listGrid}>
          {/* Dataset list */}
          <div style={styles.list}>
            {history.map((ds) => (
              <div
                key={ds.id}
                className="card"
                style={{
                  ...styles.listItem,
                  ...(selectedId === ds.id ? styles.listItemActive : {}),
                }}
                onClick={() => selectDataset(ds.id)}
              >
                <div style={styles.listItemHeader}>
                  <span style={styles.listItemName}>{ds.name}</span>
                  <span style={styles.listItemDate}>
                    {new Date(ds.uploaded_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
                <div style={styles.listItemMeta}>
                  <span style={styles.metaBadge}>{ds.total_records} records</span>
                  <span style={styles.metaBadge2}>
                    {Object.keys(ds.type_distribution).length} types
                  </span>
                </div>
                <div style={styles.listItemActions}>
                  <button
                    className="btn btn-secondary btn-sm"
                    onClick={(e) => handlePDF(ds.id, e)}
                    disabled={pdfLoading === ds.id}
                  >
                    {pdfLoading === ds.id ? '⟳' : '⬇ PDF'}
                  </button>
                  <button className="btn btn-danger btn-sm" onClick={(e) => handleDelete(ds.id, e)}>
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Detail panel */}
          <div style={styles.detailPanel}>
            {detailLoading && <div style={styles.loading}>Loading details…</div>}
            {!detailLoading && !selected && (
              <div className="card" style={styles.selectHint}>
                <span style={{ fontSize: '1.4rem' }}>👈</span>
                <p style={styles.emptyText}>Select a dataset from the list to view details.</p>
              </div>
            )}
            {!detailLoading && selected && (
              <>
                <SummaryCards summary={selected} />
                <div style={{ marginTop: 16 }}>
                  <TypeDistributionChart distribution={selected.type_distribution} />
                </div>
                <div style={{ marginTop: 16 }}>
                  <DataTable records={selected.records} />
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

const styles = {
  pageHeader: {
    marginBottom: 20,
  },
  pageTitle: {
    color: '#e8ecf0',
    fontSize: '1.3rem',
    fontWeight: 600,
  },
  pageSubtitle: {
    color: '#5a6a7d',
    fontSize: '.8rem',
  },
  loading: {
    color: '#8a9bb0',
    fontSize: '.85rem',
    padding: 20,
    textAlign: 'center',
  },
  emptyState: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: 8,
    padding: '36px 20px',
    textAlign: 'center',
  },
  emptyIcon: { fontSize: '2rem' },
  emptyText: { color: '#5a6a7d', fontSize: '.82rem', maxWidth: 340 },
  listGrid: {
    display: 'grid',
    gridTemplateColumns: '340px 1fr',
    gap: 20,
    alignItems: 'start',
  },
  list: {
    display: 'flex',
    flexDirection: 'column',
    gap: 10,
  },
  listItem: {
    padding: '14px 16px',
    cursor: 'pointer',
    transition: 'border-color .2s, background .2s',
  },
  listItemActive: {
    borderColor: 'rgba(0,200,160,.4)',
    background: 'rgba(0,200,160,.04)',
  },
  listItemHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    gap: 8,
  },
  listItemName: {
    color: '#e8ecf0',
    fontSize: '.85rem',
    fontWeight: 500,
    wordBreak: 'break-all',
  },
  listItemDate: {
    color: '#5a6a7d',
    fontSize: '.7rem',
    whiteSpace: 'nowrap',
  },
  listItemMeta: {
    display: 'flex',
    gap: 6,
    marginTop: 6,
  },
  metaBadge: {
    background: 'rgba(0,200,160,.1)',
    color: '#00c8a0',
    fontSize: '.68rem',
    padding: '2px 7px',
    borderRadius: 10,
    fontWeight: 500,
  },
  metaBadge2: {
    background: 'rgba(59,130,246,.1)',
    color: '#3b82f6',
    fontSize: '.68rem',
    padding: '2px 7px',
    borderRadius: 10,
    fontWeight: 500,
  },
  listItemActions: {
    display: 'flex',
    gap: 6,
    marginTop: 10,
  },
  detailPanel: {
    display: 'flex',
    flexDirection: 'column',
    gap: 16,
  },
  selectHint: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: 8,
    padding: '48px 24px',
    textAlign: 'center',
  },
};

export default History;
