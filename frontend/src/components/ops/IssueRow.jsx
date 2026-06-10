const SEVERITY_STYLES = {
  CRITICAL:  'bg-red-50 text-red-700 border border-red-200',
  RECURRING: 'bg-amber-50 text-amber-700 border border-amber-200',
  ONE_OFF:   'bg-gray-50 text-gray-600 border border-gray-200',
};

const CONTROL_STYLES = {
  caretaker: 'bg-blue-50 text-blue-700 border border-blue-200',
  property:  'bg-gray-50 text-gray-400 border border-gray-200',
};

export default function IssueRow({ issue }) {
  const sev = issue.severity || 'ONE_OFF';
  const ctrl = issue.caretaker_controllable;

  return (
    <div className="flex flex-col gap-1 py-2.5 border-b border-gray-50 last:border-0">
      <div className="flex items-center gap-2 flex-wrap">
        {/* Severity badge */}
        <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${SEVERITY_STYLES[sev]}`}>
          {sev}
        </span>
        {/* Caretaker / Property badge */}
        <span className={`text-xs px-2 py-0.5 rounded-full ${ctrl ? CONTROL_STYLES.caretaker : CONTROL_STYLES.property}`}>
          {ctrl ? 'CARETAKER' : 'PROPERTY'}
        </span>
        {/* Review count */}
        {issue.review_count > 1 && (
          <span className="text-xs text-gray-400">{issue.review_count} reviews</span>
        )}
        {/* Issue title */}
        <span className="text-sm font-medium text-gray-900">{issue.issue}</span>
      </div>

      {/* Supporting evidence */}
      {issue.supporting_evidence && (
        <p className="text-xs text-gray-500 italic pl-1">"{issue.supporting_evidence}"</p>
      )}

      {/* Recommended action */}
      {issue.recommended_action && (
        <p className="text-xs text-gray-600 pl-1">
          <span className="font-medium text-gray-700">Action: </span>
          {issue.recommended_action}
        </p>
      )}
    </div>
  );
}
