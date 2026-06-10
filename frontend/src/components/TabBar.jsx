const TABS = [
  { id: 'ops',       label: 'Operations',  desc: 'Priority action board' },
  { id: 'business', label: 'Business',     desc: 'Portfolio scorecard'   },
  { id: 'caretaker',label: 'Caretakers',   desc: 'Coaching digests'      },
];

export default function TabBar({ activeTab, setActiveTab }) {
  return (
    <div className="flex border-b border-gray-100 gap-1">
      {TABS.map(tab => (
        <button
          key={tab.id}
          id={`tab-${tab.id}`}
          onClick={() => setActiveTab(tab.id)}
          className={`pb-2.5 px-3 text-sm transition-colors ${
            activeTab === tab.id
              ? 'border-b-2 border-gray-900 text-gray-900 font-medium'
              : 'text-gray-400 hover:text-gray-600 cursor-pointer'
          }`}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
}
