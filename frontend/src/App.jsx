import { useState, useEffect } from 'react';
import Header from './components/Header';
import TabBar from './components/TabBar';
import OpsView from './components/ops/OpsView';
import BusinessView from './components/business/BusinessView';
import CaretakerView from './components/caretaker/CaretakerView';
import { runAnalysis, getHealth, getStatus } from './api/backendApi';

// Progress steps shown while Gemini is analyzing
const PROGRESS_STEPS = [
  'Loading 46 guest reviews across 7 properties…',
  'Filtering noise reviews (RV035, RV041)…',
  'Normalizing ratings across Airbnb / Booking / Google…',
  'Sending Serenity Villa to Gemini AI…',
  'Sending Hilltop Haven to Gemini AI…',
  'Sending Misty Estate to Gemini AI…',
  'Sending Coorg Canopy to Gemini AI…',
  'Sending Backwater Bungalow to Gemini AI…',
  'Sending Cliffside Retreat to Gemini AI…',
  'Sending Vineyard Villa to Gemini AI…',
  'Detecting cross-property patterns…',
  'Building stakeholder views…',
];

export default function App() {
  const [phase, setPhase] = useState('idle');      // 'idle' | 'analyzing' | 'done'
  const [results, setResults] = useState(null);
  const [activeTab, setActiveTab] = useState('ops');
  const [error, setError] = useState(null);
  const [stepIndex, setStepIndex] = useState(0);
  const [aiStatus, setAiStatus] = useState(null);  // null | { ai_available, reason, model }

  // Check AI availability once on mount
  useEffect(() => {
    getStatus()
      .then(data => setAiStatus(data))
      .catch(() => setAiStatus({ ai_available: false, reason: 'Backend not reachable' }));
  }, []);

  async function handleAnalyze() {
    setPhase('analyzing');
    setError(null);
    setStepIndex(0);

    // Cycle through progress steps while waiting
    const interval = setInterval(() => {
      setStepIndex(prev => Math.min(prev + 1, PROGRESS_STEPS.length - 1));
    }, 4000);

    try {
      const data = await runAnalysis();
      clearInterval(interval);
      setResults(data);
      setPhase('done');
    } catch (e) {
      clearInterval(interval);
      setError(e?.response?.data?.detail || 'Analysis failed. Make sure the backend is running at http://localhost:8000');
      setPhase('idle');
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-3xl mx-auto px-4 py-6">
        <Header />

        {/* ── IDLE STATE ─────────────────────────────────────── */}
        {phase === 'idle' && (
          <div className="text-center py-16">
            <div className="inline-flex items-center gap-2 bg-white border border-gray-200 rounded-full px-4 py-1.5 text-xs text-gray-500 mb-3 shadow-sm">
              <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
              46 reviews · 7 properties · 6 caretakers
            </div>

            {/* AI Status Badge */}
            <div className="mb-6">
              {aiStatus === null && (
                <div className="inline-flex items-center gap-2 bg-white border border-gray-100 rounded-full px-4 py-1.5 text-xs text-gray-400 shadow-sm">
                  <span className="w-1.5 h-1.5 rounded-full bg-gray-300 animate-pulse" />
                  Checking Gemini AI…
                </div>
              )}
              {aiStatus?.ai_available === true && (
                <div className="inline-flex items-center gap-2 bg-green-50 border border-green-200 rounded-full px-4 py-1.5 text-xs text-green-700 shadow-sm">
                  <span className="w-1.5 h-1.5 rounded-full bg-green-500" />
                  Gemini AI available · {aiStatus.model}
                </div>
              )}
              {aiStatus?.ai_available === false && (
                <div className="inline-flex items-center gap-2 bg-red-50 border border-red-200 rounded-full px-4 py-1.5 text-xs text-red-600 shadow-sm" title={aiStatus.reason}>
                  <span className="w-1.5 h-1.5 rounded-full bg-red-500" />
                  Gemini AI unavailable — check API key
                </div>
              )}
            </div>
            <p className="text-gray-500 text-sm mb-6 max-w-sm mx-auto">
              AI-powered review intelligence across Airbnb, Booking.com, and Google — normalized and ranked for your team.
            </p>
            <button
              id="run-analysis-btn"
              onClick={handleAnalyze}
              className="bg-gray-900 text-white px-8 py-3 rounded-lg text-sm font-medium hover:bg-gray-700 transition-colors shadow-sm"
            >
              Run Analysis ↗
            </button>
            {error && (
              <div className="mt-4 bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg px-4 py-3 max-w-md mx-auto">
                {error}
              </div>
            )}
          </div>
        )}

        {/* ── ANALYZING STATE ────────────────────────────────── */}
        {phase === 'analyzing' && (
          <div className="py-12">
            <div className="flex flex-col items-center mb-8">
              <div className="w-8 h-8 border-2 border-gray-900 border-t-transparent rounded-full animate-spin mb-4" />
              <p className="text-sm font-medium text-gray-800">AI analyzing all 7 properties…</p>
              <p className="text-xs text-gray-400 mt-1">This takes 30–60 seconds</p>
            </div>
            <div className="bg-white border border-gray-100 rounded-xl p-4 shadow-sm space-y-2">
              {PROGRESS_STEPS.map((step, i) => (
                <div
                  key={i}
                  className={`flex items-center gap-3 text-xs transition-all duration-300 ${
                    i < stepIndex ? 'text-green-600' :
                    i === stepIndex ? 'text-gray-900 font-medium' :
                    'text-gray-300'
                  }`}
                >
                  {i < stepIndex ? (
                    <span className="text-green-500 shrink-0">✓</span>
                  ) : i === stepIndex ? (
                    <span className="w-3 h-3 border border-gray-900 border-t-transparent rounded-full animate-spin shrink-0" />
                  ) : (
                    <span className="w-3 h-3 rounded-full border border-gray-200 shrink-0" />
                  )}
                  {step}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ── DONE STATE ─────────────────────────────────────── */}
        {phase === 'done' && results && (
          <>
            <div className="flex items-center justify-between mb-4">
              <TabBar activeTab={activeTab} setActiveTab={setActiveTab} />
              <button
                onClick={() => { setPhase('idle'); setResults(null); }}
                className="text-xs text-gray-400 hover:text-gray-600 transition-colors ml-4 shrink-0"
              >
                ↺ Re-run
              </button>
            </div>
            {activeTab === 'ops'       && <OpsView data={results.ops} />}
            {activeTab === 'business'  && <BusinessView data={results.business} />}
            {activeTab === 'caretaker' && <CaretakerView data={results.caretaker} />}
          </>
        )}
      </div>
    </div>
  );
}
