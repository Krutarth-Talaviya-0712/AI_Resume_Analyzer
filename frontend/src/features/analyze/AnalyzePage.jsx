import { useState, useCallback, useRef } from 'react';
import api from '../../shared/utils/api';
import ScoreRing from './components/ScoreRing';
import AnalysisReport from './components/AnalysisReport';
import JobSuggestions from './components/JobSuggestions';

// ---- Upload state machine ----
const STATES = {
  IDLE: 'IDLE',
  DRAGGING: 'DRAGGING',
  UPLOADING: 'UPLOADING',
  SUCCESS: 'SUCCESS',
  ERROR: 'ERROR',
};

const ACCEPTED_TYPES = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];

const AnalyzePage = () => {
  const [uploadState, setUploadState] = useState(STATES.IDLE);
  const [report, setReport] = useState(null);
  const [errorMessage, setErrorMessage] = useState('');
  const [activeTab, setActiveTab] = useState('report');
  const [uploadProgress, setUploadProgress] = useState(0);
  const fileInputRef = useRef(null);
  const resultsRef = useRef(null);

  const validateFile = (file) => {
    if (!file) return 'Please select a file.';
    if (!ACCEPTED_TYPES.includes(file.type) && !file.name.match(/\.(pdf|docx)$/i)) {
      return 'Only PDF and DOCX files are accepted.';
    }
    if (file.size > 5 * 1024 * 1024) {
      return 'File size must be under 5 MB.';
    }
    return null;
  };

  const runAnalysis = useCallback(async (file) => {
    const validationError = validateFile(file);
    if (validationError) {
      setErrorMessage(validationError);
      setUploadState(STATES.ERROR);
      return;
    }

    setUploadState(STATES.UPLOADING);
    setErrorMessage('');
    setUploadProgress(0);

    // Simulate incremental progress for UX while the real request is in flight
    const progressInterval = setInterval(() => {
      setUploadProgress((prev) => Math.min(prev + Math.random() * 12, 85));
    }, 300);

    try {
      const formData = new FormData();
      formData.append('resume', file);

      const response = await api.post('/api/analyze/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      clearInterval(progressInterval);
      setUploadProgress(100);

      setTimeout(() => {
        setReport(response.data);
        setUploadState(STATES.SUCCESS);
        setActiveTab('report');
        // Scroll to results
        setTimeout(() => resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 100);
      }, 300);
    } catch (err) {
      clearInterval(progressInterval);
      const msg = err.response?.data?.message || 'Analysis failed. Please try again.';
      setErrorMessage(msg);
      setUploadState(STATES.ERROR);
    }
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setUploadState(STATES.IDLE);
    const file = e.dataTransfer.files?.[0];
    if (file) runAnalysis(file);
  }, [runAnalysis]);

  const handleDragOver = (e) => {
    e.preventDefault();
    setUploadState(STATES.DRAGGING);
  };

  const handleDragLeave = () => {
    if (uploadState === STATES.DRAGGING) setUploadState(STATES.IDLE);
  };

  const handleFileInput = (e) => {
    const file = e.target.files?.[0];
    if (file) runAnalysis(file);
    e.target.value = '';
  };

  const handleReset = () => {
    setUploadState(STATES.IDLE);
    setReport(null);
    setErrorMessage('');
    setUploadProgress(0);
  };

  const isDragging = uploadState === STATES.DRAGGING;
  const isUploading = uploadState === STATES.UPLOADING;

  return (
    <div className="max-w-5xl mx-auto py-10 px-4">

      {/* Page header */}
      <div className="mb-8">
        <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight">Resume Analyzer</h1>
        <p className="text-gray-500 mt-1.5 max-w-2xl">
          Upload your resume and receive an ATS compatibility score, a full quality analysis,
          and job role suggestions matched to your skill set.
          Supports PDF and DOCX files up to 5 MB.
        </p>
      </div>

      {/* Upload zone */}
      {uploadState !== STATES.SUCCESS && (
        <div
          className={`relative rounded-2xl border-2 border-dashed transition-all duration-200 cursor-pointer
            ${isDragging ? 'border-blue-500 bg-blue-50 scale-[1.01]' : 'border-gray-300 bg-gray-50 hover:border-blue-400 hover:bg-blue-50/40'}
            ${isUploading ? 'pointer-events-none' : ''}
          `}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onClick={() => !isUploading && fileInputRef.current?.click()}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx"
            className="hidden"
            onChange={handleFileInput}
            id="resume-upload-input"
          />

          <div className="flex flex-col items-center justify-center py-16 px-8 text-center">
            {isUploading ? (
              <div className="flex flex-col items-center gap-4 w-full max-w-sm">
                <div className="w-14 h-14 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
                <p className="text-gray-700 font-semibold">Analyzing your resume...</p>
                <p className="text-xs text-gray-400">Running NLP pipeline and scoring engine</p>
                <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden mt-2">
                  <div
                    className="h-full bg-blue-600 rounded-full transition-all duration-300"
                    style={{ width: `${uploadProgress}%` }}
                  />
                </div>
                <p className="text-xs text-gray-500">{Math.round(uploadProgress)}% complete</p>
              </div>
            ) : (
              <>
                <div className="w-16 h-16 bg-blue-100 rounded-2xl flex items-center justify-center mb-4">
                  <svg className="w-8 h-8 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round"
                      d="M9 8.25H7.5a2.25 2.25 0 00-2.25 2.25v9a2.25 2.25 0 002.25 2.25h9a2.25 2.25 0 002.25-2.25v-9a2.25 2.25 0 00-2.25-2.25H15m0-3l-3-3m0 0l-3 3m3-3V15" />
                  </svg>
                </div>
                <p className="text-gray-800 font-semibold text-lg">
                  {isDragging ? 'Drop your resume here' : 'Drag and drop your resume here'}
                </p>
                <p className="text-gray-500 text-sm mt-1">or click to browse files</p>
                <p className="text-gray-400 text-xs mt-3">PDF or DOCX — maximum 5 MB</p>
              </>
            )}
          </div>
        </div>
      )}

      {/* Error state */}
      {uploadState === STATES.ERROR && (
        <div className="mt-4 flex items-start gap-3 bg-red-50 border border-red-200 rounded-xl p-4">
          <div className="w-5 h-5 rounded-full bg-red-500 text-white text-xs font-bold flex items-center justify-center flex-shrink-0 mt-0.5">
            !
          </div>
          <div>
            <p className="text-sm font-semibold text-red-700">{errorMessage}</p>
            <button onClick={handleReset} className="text-xs text-red-600 hover:underline mt-1">
              Try again
            </button>
          </div>
        </div>
      )}

      {/* Results */}
      {uploadState === STATES.SUCCESS && report && (
        <div ref={resultsRef} className="mt-2">

          {/* Result header */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
            <div>
              <h2 className="text-xl font-extrabold text-gray-900">Analysis Complete</h2>
              <p className="text-sm text-gray-400 mt-0.5 truncate max-w-xs" title={report.filename}>
                {report.filename}
              </p>
            </div>
            <button
              onClick={handleReset}
              className="inline-flex items-center gap-2 border border-gray-200 hover:border-blue-300 text-gray-600 hover:text-blue-600 text-sm font-medium px-4 py-2 rounded-xl transition-all"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
              </svg>
              Analyze Another Resume
            </button>
          </div>

          {/* Score overview */}
          <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6 mb-6">
            <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-6">Score Overview</h3>
            <div className="flex flex-wrap justify-center sm:justify-start gap-10">
              <ScoreRing
                score={report.ats_score}
                label="ATS Score"
                color={report.ats_score >= 70 ? '#22c55e' : report.ats_score >= 45 ? '#3b82f6' : '#f59e0b'}
                size={140}
                thickness={12}
              />
              <ScoreRing
                score={report.overall_score}
                label="Overall Score"
                color={report.overall_score >= 70 ? '#8b5cf6' : report.overall_score >= 45 ? '#3b82f6' : '#f59e0b'}
                size={140}
                thickness={12}
              />
              <div className="flex flex-col justify-center gap-3 min-w-[200px]">
                <div>
                  <p className="text-xs text-gray-400 font-medium mb-1">Technical Skills</p>
                  <p className="text-2xl font-extrabold text-gray-900">{(report.technical_skills || []).length}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-400 font-medium mb-1">Sections Detected</p>
                  <p className="text-2xl font-extrabold text-gray-900">{(report.detected_sections || []).length}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-400 font-medium mb-1">Job Matches</p>
                  <p className="text-2xl font-extrabold text-gray-900">{(report.job_suggestions || []).length}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Tabs */}
          <div className="border-b border-gray-200 mb-6">
            <div className="flex gap-0">
              {[
                { id: 'report', label: 'Detailed Report' },
                { id: 'jobs', label: `Job Suggestions (${(report.job_suggestions || []).length})` },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`px-5 py-3 text-sm font-semibold border-b-2 transition-colors ${
                    activeTab === tab.id
                      ? 'border-blue-600 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>
          </div>

          {/* Tab content */}
          <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6">
            {activeTab === 'report' && <AnalysisReport report={report} />}
            {activeTab === 'jobs' && <JobSuggestions suggestions={report.job_suggestions} />}
          </div>

        </div>
      )}

      {/* How it works — shown only when idle */}
      {uploadState === STATES.IDLE && (
        <div className="mt-12">
          <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-5">How the analyzer works</h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {[
              {
                step: '01',
                title: 'Text Extraction',
                desc: 'pdfplumber and python-docx extract raw text from your uploaded file.',
              },
              {
                step: '02',
                title: 'NLP Analysis',
                desc: 'spaCy detects sections, named entities, skills, and structural signals.',
              },
              {
                step: '03',
                title: 'Scoring & Matching',
                desc: 'scikit-learn TF-IDF cosine similarity ranks your fit against 30+ job role profiles.',
              },
            ].map(({ step, title, desc }) => (
              <div key={step} className="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
                <div className="text-2xl font-black text-blue-100 mb-2">{step}</div>
                <h3 className="text-sm font-bold text-gray-900 mb-1">{title}</h3>
                <p className="text-xs text-gray-500 leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      )}

    </div>
  );
};

export default AnalyzePage;
