'use client'

import { useState, useEffect, useCallback } from 'react'

// --- (All TypeScript types remain the same) ---
type JobStatus = 'idle' | 'uploading' | 'processing' | 'completed' | 'failed';
interface Job { run_id: number; status: string; }
interface JobStatusResponse { run_id: number; status: string; current_task?: string; start_time: string; end_time?: string; }
interface ResultData {
  consolidated_revenue?: { value: number; unit: string; source_page: number };
  consolidated_net_income?: { value: number; unit: string; source_page: number };
  diluted_eps?: { value: number; unit: string; source_page: number };
  top_3_segment_contributions?: Array<{ segment_name: string; percentage_contribution: number }>;
  employee_utilization?: { rate_percentage: number; source_page: number };
  key_management_risks?: Array<{ risk_summary: string }>;
}
interface TraceLog { timestamp: string; node_name: string; log_message: string; }
interface JobResult { run_id: number; status: string; filename: string; results?: ResultData; trace_logs: TraceLog[]; }


export default function ExtractionPage() {
  const [file, setFile] = useState<File | null>(null);
  const [availableFiles, setAvailableFiles] = useState<string[]>([]);
  const [selectedFile, setSelectedFile] = useState<string>('');
  
  const [job, setJob] = useState<Job | null>(null);
  const [jobStatus, setJobStatus] = useState<JobStatus>('idle');
  const [currentTask, setCurrentTask] = useState<string>('');
  
  const [result, setResult] = useState<JobResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  // --- NEW STATE FOR AD-HOC Q&A ---
  const [adHocQuestion, setAdHocQuestion] = useState('');
  const [adHocAnswer, setAdHocAnswer] = useState('');
  const [isAdHocLoading, setIsAdHocLoading] = useState(false);
  const [adHocError, setAdHocError] = useState('');

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  // --- (All existing functions remain the same) ---
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

  // --- NEW FUNCTION TO HANDLE AD-HOC QUESTIONS ---
  const handleAdHocQuery = async () => {
    if (!adHocQuestion.trim() || !selectedFile) return;
    setIsAdHocLoading(true);
    setAdHocAnswer('');
    setAdHocError('');
    try {
      const response = await fetch(`${API_URL}/api/v1/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filename: selectedFile, question: adHocQuestion }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Failed to get answer.');
      }
      setAdHocAnswer(data.answer);
    } catch (err) {
      setAdHocError(err instanceof Error ? err.message : 'An unknown error occurred.');
    } finally {
      setIsAdHocLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <h1 style={styles.header}>Financial Document Extraction Agent</h1>
      <p style={styles.subHeader}>An interactive tool to extract structured and ad-hoc data from financial reports.</p>

      {/* --- Step 1: File Management (Unchanged) --- */}
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

      {/* --- Step 2: TCS Challenge Extraction --- */}
      <div style={styles.card}>
        <div style={styles.cardHeader}><h3>Step 2: TCS Challenge: Key Metrics Extraction</h3></div>
        <div style={styles.cardBody}>
          <p style={styles.description}>Run the pre-defined extraction job to get key financial metrics from the selected document.</p>
          <button style={!selectedFile || jobStatus === 'processing' ? styles.buttonDisabled : styles.button} onClick={handleStartExtraction} disabled={!selectedFile || jobStatus === 'processing'}>
            {jobStatus === 'processing' ? 'Processing...' : `Start Challenge on ${selectedFile || '...'}`}
          </button>
        </div>
      </div>
      
      {/* --- Step 3: Monitoring (Unchanged) --- */}
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
      
      {/* --- Step 4: Results Display (Now includes Ad-Hoc Q&A) --- */}
      {result && jobStatus === 'completed' && (
        <div style={styles.card}>
            <div style={styles.cardHeader}><h3>Step 3: View Results & Ask Follow-up Questions</h3></div>
            <div style={styles.cardBody}>
                <ResultsDisplay results={result} />
                
                {/* --- NEW AD-HOC Q&A SECTION --- */}
                <div style={styles.adHocSection}>
                    <h4>Ask a Follow-up Question</h4>
                    <p style={styles.description}>Now that the document is processed, ask any question you want.</p>
                    <textarea
                        style={styles.textArea}
                        placeholder="e.g., What was the company's free cash flow in the previous year?"
                        value={adHocQuestion}
                        onChange={(e) => setAdHocQuestion(e.target.value)}
                    />
                    <button style={isAdHocLoading ? styles.buttonDisabled : styles.button} onClick={handleAdHocQuery} disabled={isAdHocLoading}>
                        {isAdHocLoading ? 'Thinking...' : 'Get Answer'}
                    </button>
                    {adHocAnswer && <div style={styles.answerBox}>{adHocAnswer}</div>}
                    {adHocError && <p style={styles.errorText}>{adHocError}</p>}
                </div>
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

// --- NEW: Nicely Formatted Structured Results Component ---
const StructuredResults = ({ results }: { results: ResultData }) => (
  <div>
    <h4>TCS Challenge: Key Metrics</h4>
    <table style={styles.table}>
      <thead>
        <tr>
          <th style={styles.th}>Metric</th>
          <th style={styles.th}>Value</th>
          <th style={styles.th}>Unit</th>
          <th style={styles.th}>Source Page</th>
        </tr>
      </thead>
      <tbody>
        {results.consolidated_revenue && (
          <tr>
            <td style={styles.td}>Consolidated Revenue</td>
            <td style={styles.td}>{results.consolidated_revenue.value.toLocaleString()}</td>
            <td style={styles.td}>{results.consolidated_revenue.unit}</td>
            <td style={styles.td}>{results.consolidated_revenue.source_page}</td>
          </tr>
        )}
        {results.consolidated_net_income && (
          <tr>
            <td style={styles.td}>Consolidated Net Income</td>
            <td style={styles.td}>{results.consolidated_net_income.value.toLocaleString()}</td>
            <td style={styles.td}>{results.consolidated_net_income.unit}</td>
            <td style={styles.td}>{results.consolidated_net_income.source_page}</td>
          </tr>
        )}
        {results.diluted_eps && (
           <tr>
            <td style={styles.td}>Diluted EPS</td>
            <td style={styles.td}>{results.diluted_eps.value}</td>
            <td style={styles.td}>{results.diluted_eps.unit}</td>
            <td style={styles.td}>{results.diluted_eps.source_page}</td>
          </tr>
        )}
        {results.employee_utilization && (
           <tr>
            <td style={styles.td}>Employee Utilization</td>
            <td style={styles.td}>{results.employee_utilization.rate_percentage}</td>
            <td style={styles.td}>%</td>
            <td style={styles.td}>{results.employee_utilization.source_page}</td>
          </tr>
        )}
      </tbody>
    </table>

    {results.top_3_segment_contributions && results.top_3_segment_contributions.length > 0 && (
      <>
        <h5 style={styles.subMetricHeader}>Top 3 Segment Contributions</h5>
        <table style={styles.table}>
           <thead><tr><th style={styles.th}>Segment</th><th style={styles.th}>Contribution (%)</th></tr></thead>
           <tbody>
            {results.top_3_segment_contributions.map((seg, i) => (
              <tr key={i}><td style={styles.td}>{seg.segment_name}</td><td style={styles.td}>{seg.percentage_contribution}</td></tr>
            ))}
           </tbody>
        </table>
      </>
    )}

    {results.key_management_risks && results.key_management_risks.length > 0 && (
      <>
        <h5 style={styles.subMetricHeader}>Key Management Risks</h5>
        <ul style={styles.riskList}>
          {results.key_management_risks.map((risk, i) => <li key={i}>{risk.risk_summary}</li>)}
        </ul>
      </>
    )}
  </div>
);


// --- MODIFIED: ResultsDisplay now uses the new component ---
const ResultsDisplay = ({ results }: { results: JobResult }) => (
    <div>
        {results.results && <StructuredResults results={results.results} />}
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


// --- (StatusIndicator component is unchanged) ---
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

// --- ADD NEW STYLES for table and Q&A section ---
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
  adHocSection: { borderTop: '1px solid #dee2e6', marginTop: '2rem', paddingTop: '1.5rem' },
  textArea: { width: '100%', minHeight: '80px', padding: '10px', borderRadius: '4px', border: '1px solid #dee2e6', fontSize: '14px', fontFamily: 'inherit', marginBottom: '1rem' },
  answerBox: { backgroundColor: '#e9ecef', padding: '1rem', borderRadius: '6px', whiteSpace: 'pre-wrap', fontFamily: 'inherit', fontSize: '14px', marginTop: '1rem', border: '1px solid #dee2e6' },
  table: { width: '100%', borderCollapse: 'collapse', marginTop: '1rem', marginBottom: '1.5rem' },
  th: { border: '1px solid #dee2e6', padding: '8px', textAlign: 'left', backgroundColor: '#f8f9fa', fontWeight: 600 },
  td: { border: '1px solid #dee2e6', padding: '8px' },
  subMetricHeader: { marginTop: '1.5rem', marginBottom: '0.5rem' },
  riskList: { paddingLeft: '20px', marginTop: '0.5rem' },
};