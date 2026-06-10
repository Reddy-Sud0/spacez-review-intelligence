const TIER_DOT = {
  good: 'bg-green-400',
  mid:  'bg-amber-400',
  bad:  'bg-red-400',
};

const TIER_TEXT = {
  good: 'text-green-700',
  mid:  'text-amber-700',
  bad:  'text-red-700',
};

export default function PortfolioTable({ rows }) {
  if (!rows || rows.length === 0) return null;

  return (
    <div className="bg-white border border-gray-100 rounded-xl shadow-sm mb-6 overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-50">
        <h2 className="text-sm font-semibold text-gray-900">Portfolio Scorecard</h2>
        <p className="text-xs text-gray-400 mt-0.5">Best rated first · All ratings normalized to /10</p>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-gray-50 text-gray-400">
              <th className="text-left px-4 py-2 font-medium">Property</th>
              <th className="text-left px-4 py-2 font-medium">Caretaker</th>
              <th className="text-center px-4 py-2 font-medium">Rating</th>
              <th className="text-center px-4 py-2 font-medium">Reviews</th>
              <th className="text-center px-4 py-2 font-medium">Response</th>
              <th className="text-center px-4 py-2 font-medium">Critical</th>
              <th className="text-center px-4 py-2 font-medium">Status</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) => (
              <tr key={row.property_id} className={`border-b border-gray-50 last:border-0 ${i % 2 === 0 ? '' : 'bg-gray-50/40'}`}>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <span className={`w-2 h-2 rounded-full shrink-0 ${TIER_DOT[row.rating_tier] || 'bg-gray-300'}`} />
                    <div>
                      <div className="font-medium text-gray-900">{row.property_name}</div>
                      <div className="text-gray-400 text-xs">{row.location}</div>
                    </div>
                  </div>
                </td>
                <td className="px-4 py-3 text-gray-600">{row.caretaker_name}</td>
                <td className="px-4 py-3 text-center">
                  <span className={`font-semibold ${TIER_TEXT[row.rating_tier]}`}>
                    {row.avg_rating}/10
                  </span>
                </td>
                <td className="px-4 py-3 text-center text-gray-600">{row.review_count}</td>
                <td className="px-4 py-3 text-center text-gray-600">{row.response_rate}%</td>
                <td className="px-4 py-3 text-center">
                  {row.critical_count > 0 ? (
                    <span className="text-red-600 font-semibold">{row.critical_count}</span>
                  ) : (
                    <span className="text-gray-300">—</span>
                  )}
                </td>
                <td className="px-4 py-3 text-center">
                  {row.has_resolved ? (
                    <span className="bg-green-50 text-green-700 border border-green-200 px-2 py-0.5 rounded-full text-xs">✓ resolved</span>
                  ) : (
                    <span className="text-gray-300 text-xs">—</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
