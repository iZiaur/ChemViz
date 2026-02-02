import React, { useState, useRef } from 'react';
import { uploadCSV } from '../services/api';

const UploadZone = ({ onUploadSuccess }) => {
  const [dragging, setDragging] = useState(false);
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState('idle'); // idle | uploading | success | error
  const [error, setError] = useState('');
  const fileRef = useRef();

  const handleFile = (f) => {
    if (!f) return;
    if (!f.name.endsWith('.csv')) {
      setError('Only .csv files are supported.');
      setStatus('error');
      return;
    }
    setFile(f);
    setStatus('idle');
    setError('');
  };

  const onDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    handleFile(e.dataTransfer.files[0]);
  };

  const upload = async () => {
    if (!file) return;
    setStatus('uploading');
    setError('');
    try {
      await uploadCSV(file);
      setStatus('success');
      setFile(null);
      onUploadSuccess();
    } catch (err) {
      const msg = err.response?.data?.error || 'Upload failed.';
      setError(msg);
      setStatus('error');
    }
  };

  const reset = () => { setFile(null); setStatus('idle'); setError(''); };

  return (
    <div className="card" style={styles.card}>
      <h3 style={styles.title}>
        <span style={styles.titleIcon}>⬆</span>
        Upload Equipment Data
      </h3>

      {/* Drop zone */}
      <div
        style={{
          ...styles.dropzone,
          ...(dragging ? styles.dropzoneActive : {}),
          ...(status === 'error' ? styles.dropzoneError : {}),
        }}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        onClick={() => fileRef.current.click()}
      >
        <input ref={fileRef} type="file" accept=".csv" style={{ display: 'none' }} onChange={(e) => handleFile(e.target.files[0])} />

        {file ? (
          <div style={styles.filePreview}>
            <span style={styles.fileIcon}>📄</span>
            <div>
              <div style={styles.fileName}>{file.name}</div>
              <div style={styles.fileSize}>{(file.size / 1024).toFixed(1)} KB</div>
            </div>
            <button style={styles.removeBtn} onClick={(e) => { e.stopPropagation(); reset(); }}>✕</button>
          </div>
        ) : (
          <div style={styles.placeholder}>
            <span style={styles.placeholderIcon}>⬇</span>
            <span style={styles.placeholderText}>Drag & drop your <strong>.csv</strong> file here</span>
            <span style={styles.placeholderSub}>or click to browse</span>
          </div>
        )}
      </div>

      {/* Error */}
      {error && <div style={styles.errorBox}>{error}</div>}

      {/* Success */}
      {status === 'success' && (
        <div style={styles.successBox}>✓ Dataset uploaded and analyzed successfully!</div>
      )}

      {/* Actions */}
      <div style={styles.actions}>
        <button
          className="btn btn-primary"
          disabled={!file || status === 'uploading'}
          onClick={upload}
          style={styles.uploadBtn}
        >
          {status === 'uploading' ? '⟳ Uploading…' : 'Upload & Analyze'}
        </button>

        {/* Sample download hint */}
        <span style={styles.sampleHint}>
          Need test data? Place <code style={styles.code}>sample_equipment_data.csv</code> in your folder.
        </span>
      </div>
    </div>
  );
};

const styles = {
  card: { padding: 20 },
  title: {
    color: '#e8ecf0',
    fontSize: '.95rem',
    fontWeight: 600,
    marginBottom: 14,
    display: 'flex',
    alignItems: 'center',
    gap: 8,
  },
  titleIcon: {
    width: 28,
    height: 28,
    borderRadius: 6,
    background: 'rgba(0,200,160,.12)',
    color: '#00c8a0',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '.85rem',
  },
  dropzone: {
    border: '2px dashed rgba(255,255,255,.12)',
    borderRadius: 10,
    padding: '28px 20px',
    cursor: 'pointer',
    transition: 'border-color .2s, background .2s',
    background: 'rgba(255,255,255,.02)',
    minHeight: 120,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  dropzoneActive: {
    borderColor: '#00c8a0',
    background: 'rgba(0,200,160,.06)',
  },
  dropzoneError: {
    borderColor: 'rgba(239,68,68,.4)',
  },
  placeholder: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: 6,
  },
  placeholderIcon: {
    fontSize: '1.6rem',
    color: '#5a6a7d',
  },
  placeholderText: {
    color: '#8a9bb0',
    fontSize: '.82rem',
  },
  placeholderSub: {
    color: '#5a6a7d',
    fontSize: '.75rem',
  },
  filePreview: {
    display: 'flex',
    alignItems: 'center',
    gap: 12,
    width: '100%',
  },
  fileIcon: { fontSize: '1.4rem' },
  fileName: { color: '#e8ecf0', fontSize: '.84rem', fontWeight: 500 },
  fileSize: { color: '#5a6a7d', fontSize: '.72rem' },
  removeBtn: {
    marginLeft: 'auto',
    background: 'none',
    border: 'none',
    color: '#5a6a7d',
    cursor: 'pointer',
    fontSize: '.85rem',
    padding: '4px 8px',
    borderRadius: 4,
  },
  errorBox: {
    background: 'rgba(239,68,68,.1)',
    border: '1px solid rgba(239,68,68,.25)',
    borderRadius: 6,
    padding: '8px 12px',
    color: '#ef4444',
    fontSize: '.8rem',
    marginTop: 10,
  },
  successBox: {
    background: 'rgba(0,200,160,.1)',
    border: '1px solid rgba(0,200,160,.25)',
    borderRadius: 6,
    padding: '8px 12px',
    color: '#00c8a0',
    fontSize: '.8rem',
    marginTop: 10,
  },
  actions: {
    marginTop: 14,
    display: 'flex',
    flexDirection: 'column',
    gap: 10,
  },
  uploadBtn: {
    justifyContent: 'center',
    width: '100%',
    padding: '10px 0',
  },
  sampleHint: {
    color: '#5a6a7d',
    fontSize: '.72rem',
    textAlign: 'center',
  },
  code: {
    background: 'rgba(255,255,255,.08)',
    padding: '1px 5px',
    borderRadius: 3,
    color: '#00c8a0',
    fontFamily: 'JetBrains Mono, monospace',
    fontSize: '.7rem',
  },
};

export default UploadZone;
