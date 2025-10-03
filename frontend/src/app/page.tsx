'use client'

import { useState, useEffect, useCallback } from 'react'

// --- (All TypeScript types, just add current_task to JobStatusResponse) ---
type JobStatus = 'idle' | 'uploading' | 'processing' | 'completed' | 'failed';

interface Job { 
  run_id: number; 
  status: string; 
}

interface JobStatusResponse { 
  run_id: number; 
  status: string; 
  current_task?: string; 
  start_time: string;
  end_time?: string;
}

interface ResultData {
  consolidated_revenue?: { value: number; unit: string; source_page: number };
  consolidated_net_income?: { value: number; unit: string; source_page: number };
  diluted_eps?: { value: number; unit: string; source_page: number };
  top_3_segment_contributions?: Array<{ segment: string; percentage: number }>;
  employee_utilization?: { value: number; unit: string; source_page: number };
  key_management_risks?: Array<{ risk: string; description: string }>;
}

interface TraceLog {
  timestamp: string;
  node_name: string;
  log_message: string;
}

interface JobResult {
  run_id: number;
  status: string;
  filename: string;
  results?: ResultData;
  trace_logs: TraceLog[];
}

export default function ExtractionPage() {
  const [file, setFile] = useState<File | null>(null);
  const [availableFiles, setAvailableFiles] = useState<string[]>([]);
  const [selectedFile, setSelectedFile] = useState<string>('');
  
  const [job, setJob] = useState<Job | null>(null);
  const [jobStatus, setJobStatus] = useState<JobStatus>('idle');
  const [currentTask, setCurrentTask] = useState<string>('');
  
  const [result, setResult] = useState<JobResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  // --- NEW: Fetch available documents on component mount ---
  const fetchAvailableFiles = useCallback(async () => {
    try {
      const response = await fetch(`${API_URL}/api/v1/documents`);
      if (!response.ok) throw new Error('Failed to fetch file list.');
      const data = await response.json();
      setAvailableFiles(data.filenames);
      if (data.filenames.length > 0) {
        setSelectedFile(data.filenames[0]);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not fetch file list.');
    }
  }, [API_URL]);

  // Function to fetch the final results
  const fetchResults = useCallback(async (runId: number) => {
    try {
      const response = await fetch(`${API_URL}/api/v1/extractions/${runId}/results`);
      if (!response.ok) {
        throw new Error('Failed to fetch results.');
      }
      const data = await response.json();
      setResult(data);
    } catch (err) {
       setError(err instanceof Error ? err.message : 'An unknown error occurred fetching results.');
       setJobStatus('failed');
    }
  }, [API_URL]);

  useEffect(() => {
    fetchAvailableFiles();
  }, [fetchAvailableFiles]);

  // --- NEW: Handle file upload ---
  const handleFileUpload = async () => {
    if (!file) return;
    setJobStatus('uploading');
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${API_URL}/api/v1/documents/upload`, {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'File upload failed.');
      }
      setFile(null); // Clear the file input
      await fetchAvailableFiles(); // Refresh the list
      setSelectedFile(data.filename); // Select the newly uploaded file
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred.');
    } finally {
      setJobStatus('idle');
    }
  };

  const handleStartExtraction = async () => {
    if (!selectedFile) {
      setError('Please select a file to process.');
      return;
    }
    setJobStatus('processing');
    setCurrentTask('Initializing agent...');
    setError(null);
    setResult(null);
    setJob(null);

    try {
      const response = await fetch(`${API_URL}/api/v1/extract`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filename: selectedFile }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Failed to start job.');
      }
      setJob({ run_id: data.run_id, status: data.status });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred.');
      setJobStatus('failed');
    }
  };

  // --- MODIFIED: Poll Job Status to include current_task ---
  const pollJobStatus = useCallback(async () => {
    if (!job || jobStatus !== 'processing') return;
    try {
      const response = await fetch(`${API_URL}/api/v1/extractions/${job.run_id}/status`);
      if (!response.ok) throw new Error('Failed to fetch job status.');
      const data: JobStatusResponse = await response.json();

      setCurrentTask(data.current_task || '...');

      if (data.status === 'completed' || data.status === 'failed') {
        setJobStatus(data.status);
        if (data.status === 'completed') fetchResults(job.run_id);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Polling failed.');
      setJobStatus('failed');
    }
  }, [job, jobStatus, API_URL, fetchResults]);
  
  useEffect(() => {
    if (jobStatus === 'processing') {
      const intervalId = setInterval(pollJobStatus, 3000); // Poll every 3 seconds
      return () => clearInterval(intervalId); // Cleanup on component unmount
    }
  }, [jobStatus, pollJobStatus]);
  
  return (
    <div style={styles.container}>
      <h1 style={styles.header}>Financial Document Extraction Agent</h1>
      <p style={styles.subHeader}>
        Using a multi-modal AI agent to extract structured data from financial reports.
      </p>

      {/* --- NEW FILE MANAGEMENT SECTION --- */}
      <div style={styles.card}>
        <div style={styles.cardHeader}><h3>Step 1: Select or Upload a Document</h3></div>
        <div style={styles.cardBody}>
          <div style={styles.formGroup}>
            <label>Select an existing document:</label>
            <select
              style={styles.select}
              value={selectedFile}
              onChange={(e) => setSelectedFile(e.target.value)}
              disabled={availableFiles.length === 0}
            >
              {availableFiles.length > 0 ? (
                availableFiles.map(f => <option key={f} value={f}>{f}</option>)
              ) : (
                <option>No documents found</option>
              )}
            </select>
          </div>
          <div style={styles.formGroup}>
            <label>Or upload a new PDF:</label>
            <input 
              type="file" 
              accept=".pdf" 
              onChange={(e) => setFile(e.target.files ? e.target.files[0] : null)} 
              style={styles.fileInput}
            />
            <button
              style={!file || jobStatus === 'uploading' ? styles.buttonDisabled : styles.button}
              onClick={handleFileUpload}
              disabled={!file || jobStatus === 'uploading'}
            >
              {jobStatus === 'uploading' ? 'Uploading...' : 'Upload'}
            </button>
          </div>
        </div>
      </div>

      {/* --- MODIFIED EXTRACTION SECTION --- */}
      <div style={styles.card}>
        <div style={styles.cardHeader}><h3>Step 2: Start Extraction</h3></div>
        <div style={styles.cardBody}>
          <p style={styles.description}>
            {selectedFile ? `Ready to extract from: ${selectedFile}` : 'Please select a file first.'}
          </p>
          <button
            style={!selectedFile || jobStatus === 'processing' ? styles.buttonDisabled : styles.button}
            onClick={handleStartExtraction}
            disabled={!selectedFile || jobStatus === 'processing'}
          >
            {jobStatus === 'processing' ? 'Processing...' : `Extract from ${selectedFile || 'Selected File'}`}
          </button>
        </div>
      </div>
      
      {/* --- MODIFIED MONITORING SECTION --- */}
      {job && (
        <div style={styles.card}>
            <div style={styles.cardHeader}><h3>Step 3: Monitor Agent Progress</h3></div>
            <div style={styles.cardBody}>
                <StatusIndicator status={jobStatus} currentTask={currentTask} />
                {error && <p style={{...styles.errorText, marginTop: '1rem'}}>{error}</p>}
                <p style={styles.jobInfo}>Job ID: {job.run_id}</p>
            </div>
        </div>
      )}
      
      {result && jobStatus === 'completed' && (
        <div style={styles.card}>
            <div style={styles.cardHeader}>
                <h3>Step 4: View Results</h3>
            </div>
            <div style={styles.cardBody}>
                <ResultsDisplay results={result} />
            </div>
        </div>
      )}

      {error && !job && (
        <div style={styles.card}>
          <div style={styles.cardHeader}><h3>Error</h3></div>
          <div style={styles.cardBody}>
            <p style={styles.errorText}>{error}</p>
          </div>
        </div>
      )}
    </div>
  );
}

// --- MODIFIED StatusIndicator COMPONENT ---
const StatusIndicator = ({ status, currentTask }: { status: JobStatus, currentTask: string }) => {
  const statusInfo = {
    processing: { text: currentTask || 'Agent is processing...', color: '#856404', bg: '#fff3cd' },
    completed: { text: 'Extraction complete!', color: '#155724', bg: '#d4edda' },
    failed: { text: 'Extraction failed.', color: '#721c24', bg: '#f8d7da' },
    uploading: { text: 'Uploading file...', color: '#856404', bg: '#fff3cd' },
    idle: {text: '', color: '', bg: ''}
  };
  
  if (statusInfo[status].text) {
    return (
      <div style={{...styles.statusBox, backgroundColor: statusInfo[status].bg, color: statusInfo[status].color }}>
        {statusInfo[status].text}
      </div>
    );
  }
  return null;
};

// --- (ResultsDisplay component is unchanged) ---
const ResultsDisplay = ({ results }: { results: JobResult }) => (
    <div>
        <h4>Extracted Key Metrics:</h4>
        <pre style={styles.codeBlock}>
            {JSON.stringify(results.results, null, 2)}
        </pre>
        <h4 style={{marginTop: '20px'}}>Agent Reasoning Trace:</h4>
        <div style={styles.logsContainer}>
            {results.trace_logs.map((log, index) => (
                <div key={index} style={styles.logEntry}>
                    <strong>{log.node_name}</strong>
                    <pre style={styles.logMessage}>{log.log_message}</pre>
                </div>
            ))}
        </div>
    </div>
);

// --- ENHANCED INLINE STYLES ---
const styles: { [key: string]: React.CSSProperties } = {
  container: { width: '100%', maxWidth: '900px', padding: '20px' },
  header: { textAlign: 'center', fontSize: '2rem', marginBottom: '0.5rem', color: '#2c3e50' },
  subHeader: { textAlign: 'center', color: '#6c757d', marginBottom: '2rem', fontSize: '1.1rem' },
  card: { backgroundColor: '#ffffff', border: '1px solid #dee2e6', borderRadius: '8px', marginBottom: '1.5rem', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' },
  cardHeader: { padding: '1rem 1.5rem', backgroundColor: '#f8f9fa', borderBottom: '1px solid #dee2e6', borderRadius: '8px 8px 0 0' },
  cardBody: { padding: '1.5rem' },
  description: { marginBottom: '1rem', color: '#495057' },
  button: { backgroundColor: '#007bff', color: 'white', border: 'none', padding: '10px 20px', borderRadius: '6px', fontSize: '16px', cursor: 'pointer', transition: 'background-color 0.2s' },
  buttonDisabled: { backgroundColor: '#6c757d', color: 'white', border: 'none', padding: '10px 20px', borderRadius: '6px', fontSize: '16px', cursor: 'not-allowed' },
  statusBox: { padding: '1rem', borderRadius: '6px', fontWeight: 600, marginBottom: '1rem', fontSize: '14px' },
  errorText: { color: '#721c24', backgroundColor: '#f8d7da', padding: '0.75rem', borderRadius: '4px', border: '1px solid #f5c6cb' },
  jobInfo: { color: '#6c757d', fontSize: '14px' },
  codeBlock: { backgroundColor: '#e9ecef', padding: '1rem', borderRadius: '6px', whiteSpace: 'pre-wrap', fontFamily: 'monospace', fontSize: '14px', maxHeight: '300px', overflow: 'auto' },
  logsContainer: { maxHeight: '400px', overflowY: 'auto', border: '1px solid #dee2e6', borderRadius: '6px', padding: '1rem', backgroundColor: '#f8f9fa' },
  logEntry: { marginBottom: '1rem', borderBottom: '1px solid #dee2e6', paddingBottom: '1rem' },
  logMessage: { whiteSpace: 'pre-wrap', fontFamily: 'monospace', fontSize: '13px', color: '#495057', marginTop: '0.5rem' },
  formGroup: { marginBottom: '1rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' },
  select: { padding: '8px 12px', borderRadius: '4px', border: '1px solid #dee2e6', fontSize: '14px', backgroundColor: 'white' },
  fileInput: { padding: '8px', borderRadius: '4px', border: '1px solid #dee2e6', marginBottom: '0.5rem' },
};