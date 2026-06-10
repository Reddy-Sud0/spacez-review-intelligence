import IssueRow from './IssueRow';

const TIER_STYLES = {
  good: 'bg-green-50 text-green-700 border-green-200',
  mid:  'bg-amber-50 text-amber-700 border-amber-200',
  bad:  'bg-red-50 text-red-700 border-red-200',
};

const PLATFORM_ICONS = {
  'Airbnb':      '🏠',
  'Booking.com': '🔵',
  'Google':      '🔍',
};

export default function PropertyCard({ prop }) {
  const tier = prop.rating_tier || 'mid';
  const tierStyle = TIER_STYLES[tier];

  return (
    <div className="bg-white border border-gray-100 rounded-xl p-4 mb-3 shadow-sm">
      {/* ── Card Header ── */}
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap mb-0.5">
            <h2 className="text-sm font-semibold text-gray-900">{prop.property_name}</h2>

            {/* Rating badge */}
            <span className={`text-xs font-semibold px-2 py-0.5 rounded-full border ${tierStyle}`}>
              {prop.avg_normalized_rating}/10
            </span>

            {/* Resolved badge */}
            {prop.has_resolved_issue && (
              <span className="text-xs bg-green-50 text-green-700 border border-green-200 px-2 py-0.5 rounded-full">
                ✓ resolved
              </span>
            )}

            {/* API error warning */}
            {prop.api_error && (
              <span className="text-xs bg-amber-50 text-amber-700 border border-amber-200 px-2 py-0.5 rounded-full">
                ⚠ AI unavailable
              </span>
            )}
          </div>

          <p className="text-xs text-gray-400">
            {prop.location} · {prop.caretaker_name} · {prop.review_count} reviews
          </p>
        </div>

        {/* Platform icons + response rate */}
        <div className="flex flex-col items-end gap-1 shrink-0">
          <div className="flex gap-1">
            {(prop.platforms || []).map(p => (
              <span key={p} title={p} className="text-sm">{PLATFORM_ICONS[p] || '📝'}</span>
            ))}
          </div>
          <span className="text-xs text-gray-400">{prop.response_rate}% responded</span>
        </div>
      </div>

      {/* ── Cross-property caretaker alert ── */}
      {prop.is_cross_property_caretaker && prop.cross_property_pattern && (
        <div className="bg-blue-50 text-blue-800 border border-blue-200 rounded-lg p-3 mb-3 text-xs">
          <span className="font-semibold">⚠ Cross-property pattern · </span>
          {prop.cross_property_pattern}
        </div>
      )}

      {/* ── Resolved issue note ── */}
      {prop.has_resolved_issue && prop.resolved_issue_note && (
        <div className="bg-green-50 border-l-2 border-green-400 p-2 rounded mb-3 text-xs text-green-800">
          ✓ {prop.resolved_issue_note}
        </div>
      )}

      {/* ── Issues list ── */}
      {prop.recurring_issues && prop.recurring_issues.length > 0 ? (
        <div className="mb-3">
          <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">Issues</p>
          <div>
            {prop.recurring_issues.map((issue, i) => (
              <IssueRow key={i} issue={issue} />
            ))}
          </div>
        </div>
      ) : (
        <p className="text-xs text-gray-400 mb-3 italic">No recurring issues flagged.</p>
      )}

      {/* ── What works well ── */}
      {prop.what_works_well && prop.what_works_well.length > 0 && (
        <div className="bg-green-50 border-l-2 border-green-400 p-2 rounded mb-2">
          <p className="text-xs font-medium text-green-800 mb-1">What works well</p>
          <ul className="space-y-0.5">
            {prop.what_works_well.map((item, i) => (
              <li key={i} className="text-xs text-green-800">· {item}</li>
            ))}
          </ul>
        </div>
      )}

      {/* ── Noise excluded ── */}
      {prop.noise_excluded_reasons && prop.noise_excluded_reasons.length > 0 && (
        <div className="bg-gray-50 border-l-2 border-gray-300 p-2 rounded mt-2">
          <p className="text-xs font-medium text-gray-500 mb-1">Excluded from analysis</p>
          <ul className="space-y-0.5">
            {prop.noise_excluded_reasons.map((r, i) => (
              <li key={i} className="text-xs text-gray-400">· {r}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
