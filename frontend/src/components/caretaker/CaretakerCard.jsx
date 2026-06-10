const TIER_STYLES = {
  good: 'bg-green-50 text-green-700 border-green-200',
  mid:  'bg-amber-50 text-amber-700 border-amber-200',
  bad:  'bg-red-50 text-red-700 border-red-200',
};

export default function CaretakerCard({ ct }) {
  const tier = ct.rating_tier || 'mid';

  return (
    <div className="bg-white border border-gray-100 rounded-xl p-4 mb-3 shadow-sm">
      {/* ── Header ── */}
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap mb-0.5">
            <h2 className="text-sm font-semibold text-gray-900">{ct.caretaker_name}</h2>

            {/* Hospitality score badge */}
            <span className={`text-xs font-semibold px-2 py-0.5 rounded-full border ${TIER_STYLES[tier]}`}>
              {ct.hospitality_score}/10
            </span>

            {/* Multi-property tag */}
            {ct.is_multi_property && (
              <span className="text-xs bg-blue-50 text-blue-700 border border-blue-200 px-2 py-0.5 rounded-full">
                Multi-property
              </span>
            )}
          </div>

          <p className="text-xs text-gray-400">
            {ct.properties.join(' · ')} · {ct.total_reviews} reviews
          </p>
          <p className="text-xs text-gray-400 mt-0.5 italic">
            Score based on caretaker-controllable reviews only
          </p>
        </div>
      </div>

      {/* ── Cross-property warning ── */}
      {ct.cross_property_warning && (
        <div className="bg-blue-50 text-blue-800 border border-blue-200 rounded-lg p-3 mb-3 text-xs">
          <span className="font-semibold">⚠ Cross-property pattern · </span>
          {ct.cross_property_warning}
        </div>
      )}

      {/* ── What guests loved ── */}
      {ct.what_guests_loved && ct.what_guests_loved.length > 0 && (
        <div className="mb-3">
          <p className="text-xs font-medium text-gray-700 mb-1.5">💬 What guests loved</p>
          <div className="space-y-1">
            {ct.what_guests_loved.map((quote, i) => (
              <div key={i} className="bg-green-50 border-l-2 border-green-400 p-2 rounded text-xs text-green-800 italic">
                "{quote}"
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── One thing to improve ── */}
      {ct.one_thing_to_improve && (
        <div className="mb-3">
          <p className="text-xs font-medium text-gray-700 mb-1">🎯 One thing to improve</p>
          <div className="bg-amber-50 border-l-2 border-amber-400 p-2 rounded text-xs text-amber-800">
            {ct.one_thing_to_improve}
          </div>
        </div>
      )}

      {/* ── Property-level issues (flagged to ops, not in score) ── */}
      {ct.property_fault_issues && ct.property_fault_issues.length > 0 && (
        <div>
          <p className="text-xs font-medium text-gray-500 mb-1">🏗 Flagged to ops (not in your score)</p>
          <div className="bg-gray-50 border-l-2 border-gray-300 p-2 rounded">
            <ul className="space-y-0.5">
              {ct.property_fault_issues.map((issue, i) => (
                <li key={i} className="text-xs text-gray-500">· {issue}</li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}
