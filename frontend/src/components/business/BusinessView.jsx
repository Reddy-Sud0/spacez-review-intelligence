import SummaryMetrics from './SummaryMetrics';
import PortfolioTable from './PortfolioTable';
import SignalCards from './SignalCards';

export default function BusinessView({ data }) {
  if (!data) return <p className="text-sm text-gray-400 py-8 text-center">No business data returned.</p>;

  return (
    <div className="mt-4">
      <div className="mb-4">
        <h1 className="text-sm font-semibold text-gray-900">Business Portfolio Overview</h1>
        <p className="text-xs text-gray-400 mt-0.5">
          Normalized ratings · {data.total_properties} properties · For weekly review
        </p>
      </div>

      <SummaryMetrics data={data} />
      <PortfolioTable rows={data.portfolio_rows} />
      <SignalCards signals={data.signals} />
    </div>
  );
}
