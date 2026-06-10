const SIGNAL_STYLES = {
  STAR:     { bg: 'bg-amber-50 border-amber-200',  icon: '⭐', label: 'STAR PERFORMER',  text: 'text-amber-800' },
  ACTION:   { bg: 'bg-red-50 border-red-200',      icon: '🚨', label: 'ACTION REQUIRED', text: 'text-red-800'   },
  WATCH:    { bg: 'bg-orange-50 border-orange-200', icon: '👁', label: 'WATCH',           text: 'text-orange-800'},
  RESOLVED: { bg: 'bg-green-50 border-green-200',  icon: '✅', label: 'RESOLVED',        text: 'text-green-800' },
  NOTE:     { bg: 'bg-gray-50 border-gray-200',    icon: '📌', label: 'NOTE',            text: 'text-gray-700'  },
};

export default function SignalCards({ signals }) {
  if (!signals || signals.length === 0) return null;

  return (
    <div className="mb-4">
      <h2 className="text-sm font-semibold text-gray-900 mb-3">Strategic Signals</h2>
      <div className="space-y-2">
        {signals.map((sig, i) => {
          const style = SIGNAL_STYLES[sig.type] || SIGNAL_STYLES.NOTE;
          return (
            <div key={i} className={`border rounded-xl p-3 ${style.bg}`}>
              <div className="flex items-start gap-2">
                <span className="text-base shrink-0 mt-0.5">{style.icon}</span>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap mb-0.5">
                    <span className={`text-xs font-semibold uppercase tracking-wide ${style.text}`}>
                      {style.label}
                    </span>
                    <span className={`text-xs font-medium ${style.text} opacity-70`}>· {sig.property}</span>
                  </div>
                  <p className={`text-xs ${style.text}`}>{sig.message}</p>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
