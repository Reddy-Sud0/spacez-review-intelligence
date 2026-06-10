import PropertyCard from './PropertyCard';

export default function OpsView({ data }) {
  if (!data || data.length === 0) {
    return <p className="text-sm text-gray-400 py-8 text-center">No property data returned.</p>;
  }

  const criticalCount = data.reduce(
    (acc, p) => acc + (p.recurring_issues || []).filter(i => i.severity === 'CRITICAL').length, 0
  );

  return (
    <div className="mt-4">
      {/* Section header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-sm font-semibold text-gray-900">Operations Priority Board</h1>
          <p className="text-xs text-gray-400 mt-0.5">Sorted worst-first · Act on critical issues today</p>
        </div>
        {criticalCount > 0 && (
          <span className="bg-red-50 text-red-700 border border-red-200 text-xs font-medium px-3 py-1 rounded-full">
            {criticalCount} CRITICAL
          </span>
        )}
      </div>

      {/* Property cards — already sorted worst-first by backend */}
      {data.map(prop => (
        <PropertyCard key={prop.property_id} prop={prop} />
      ))}
    </div>
  );
}
