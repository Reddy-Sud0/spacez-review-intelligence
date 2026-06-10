import CaretakerCard from './CaretakerCard';

export default function CaretakerView({ data }) {
  if (!data || data.length === 0) {
    return <p className="text-sm text-gray-400 py-8 text-center">No caretaker data returned.</p>;
  }

  const multiProperty = data.filter(ct => ct.is_multi_property);
  const avgScore = data.length
    ? (data.reduce((s, ct) => s + ct.hospitality_score, 0) / data.length).toFixed(1)
    : 0;

  return (
    <div className="mt-4">
      {/* Section header */}
      <div className="flex items-start justify-between mb-4">
        <div>
          <h1 className="text-sm font-semibold text-gray-900">Caretaker Coaching Digests</h1>
          <p className="text-xs text-gray-400 mt-0.5">
            Hospitality-only scores · Infrastructure issues excluded from rating
          </p>
        </div>
        <div className="text-right shrink-0">
          <div className="text-sm font-semibold text-gray-900">{avgScore}/10</div>
          <div className="text-xs text-gray-400">team avg</div>
        </div>
      </div>

      {/* Fairness note */}
      <div className="bg-blue-50 border border-blue-100 rounded-lg p-3 mb-4 text-xs text-blue-800">
        <span className="font-semibold">Fairness guarantee: </span>
        WiFi failures, road conditions, listing photos, mosquitoes, and humidity are excluded from caretaker scores — these are property/ops responsibilities. Each caretaker is scored only on what they can control.
      </div>

      {/* Multi-property alert summary */}
      {multiProperty.length > 0 && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 mb-4 text-xs text-amber-800">
          <span className="font-semibold">⚠ Multi-property caretaker alert: </span>
          {multiProperty.map(ct => ct.caretaker_name).join(', ')} manage{multiProperty.length === 1 ? 's' : ''} multiple properties.
          Issues that follow a caretaker across properties are flagged on both cards.
        </div>
      )}

      {/* Caretaker cards — sorted best score first by backend */}
      {data.map(ct => (
        <CaretakerCard key={ct.caretaker_id} ct={ct} />
      ))}
    </div>
  );
}
