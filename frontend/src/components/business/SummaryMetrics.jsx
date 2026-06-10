const TIER_STYLES = {
  good: 'text-green-700 bg-green-50',
  mid:  'text-amber-700 bg-amber-50',
  bad:  'text-red-700 bg-red-50',
};

export default function SummaryMetrics({ data }) {
  const tier = data.portfolio_avg >= 7.5 ? 'good' : data.portfolio_avg >= 5.5 ? 'mid' : 'bad';

  const metrics = [
    {
      label: 'Portfolio Avg',
      value: `${data.portfolio_avg}/10`,
      sub: 'normalized across all platforms',
      highlight: TIER_STYLES[tier],
    },
    {
      label: 'Response Rate',
      value: `${data.response_rate}%`,
      sub: 'host responses to reviews',
      highlight: data.response_rate >= 60 ? 'text-green-700 bg-green-50' : 'text-amber-700 bg-amber-50',
    },
    {
      label: 'Properties',
      value: data.total_properties,
      sub: 'in portfolio',
      highlight: 'text-gray-700 bg-gray-50',
    },
    {
      label: 'Critical Issues',
      value: data.critical_issues_count,
      sub: 'need immediate action',
      highlight: data.critical_issues_count > 0 ? 'text-red-700 bg-red-50' : 'text-green-700 bg-green-50',
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
      {metrics.map(m => (
        <div key={m.label} className={`rounded-lg p-4 ${m.highlight}`}>
          <div className="text-xl font-bold">{m.value}</div>
          <div className="text-xs font-medium mt-0.5">{m.label}</div>
          <div className="text-xs opacity-60 mt-0.5">{m.sub}</div>
        </div>
      ))}
    </div>
  );
}
