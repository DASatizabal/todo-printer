const CATEGORIES = [
  { value: null, label: 'All' },
  { value: 'work', label: 'Work', active: 'bg-blue-600 text-white' },
  { value: 'school', label: 'School', active: 'bg-teal-600 text-white' },
  { value: 'personal', label: 'Personal', active: 'bg-orange-600 text-white' },
];

const SORT_OPTIONS = [
  { value: 'sort_order', label: 'Manual' },
  { value: 'priority', label: 'Priority' },
  { value: 'due_date', label: 'Due Date' },
  { value: 'category', label: 'Category' },
];

export default function FilterBar({
  filter,
  onCategoryChange,
  onSortChange,
  showArchive,
  onToggleArchive,
  multiSelect,
  onToggleMultiSelect,
  selectedCount,
  onAddClick,
  onImport,
  onSync,
  syncPending,
  syncing,
  onDailyTicket,
  onPreview,
  onPrintAll,
  onPrintSelected,
  onBulkArchive,
}) {
  return (
    <div className="px-4 py-3 space-y-2.5 border-b border-gray-800">
      {/* Row 1: category filters + sort */}
      <div className="flex flex-wrap items-center gap-2">
        {CATEGORIES.map((cat) => {
          const isActive = filter.category === cat.value;
          return (
            <button
              key={cat.value ?? 'all'}
              onClick={() => onCategoryChange(cat.value)}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? (cat.active || 'bg-white text-gray-900')
                  : 'bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-gray-200'
              }`}
            >
              {cat.label}
            </button>
          );
        })}

        <select
          value={filter.sortBy}
          onChange={(e) => onSortChange(e.target.value)}
          className="ml-auto bg-gray-800 text-gray-400 text-sm rounded-lg px-3 py-1.5 border border-gray-700 focus:outline-none focus:border-gray-500"
        >
          {SORT_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>Sort: {opt.label}</option>
          ))}
        </select>
      </div>

      {/* Row 2: actions */}
      <div className="flex flex-wrap items-center gap-2">
        <button
          onClick={onAddClick}
          className="px-3 py-1.5 rounded-lg text-sm font-medium bg-emerald-600 text-white hover:bg-emerald-500 transition-colors"
        >
          + Add Task
        </button>

        <button
          onClick={onImport}
          className="px-3 py-1.5 rounded-lg text-sm font-medium bg-cyan-700 text-cyan-100 hover:bg-cyan-600 transition-colors"
        >
          Import
        </button>

        <button
          onClick={onToggleArchive}
          className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
            showArchive
              ? 'bg-purple-600 text-white'
              : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
          }`}
        >
          {showArchive ? 'Back to Open' : 'View Archive'}
        </button>

        <button
          onClick={onToggleMultiSelect}
          className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
            multiSelect
              ? 'bg-indigo-600 text-white'
              : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
          }`}
        >
          {multiSelect ? `Selected (${selectedCount})` : 'Select'}
        </button>

        <button
          onClick={onSync}
          disabled={syncing}
          className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
            syncing
              ? 'bg-sky-800 text-sky-300 animate-pulse'
              : syncPending > 0
                ? 'bg-sky-600 text-white hover:bg-sky-500'
                : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
          }`}
        >
          {syncing ? 'Syncing...' : syncPending > 0 ? `Sync (${syncPending})` : 'Sync'}
        </button>

        <div className="flex items-center gap-2 ml-auto">
          {multiSelect && selectedCount > 0 && (
            <>
              {!showArchive && (
                <button
                  onClick={onBulkArchive}
                  className="px-3 py-1.5 rounded-lg text-sm font-medium bg-amber-600 text-white hover:bg-amber-500 transition-colors"
                >
                  Archive ({selectedCount})
                </button>
              )}
              <button
                onClick={onPrintSelected}
                className="px-3 py-1.5 rounded-lg text-sm font-medium bg-violet-600 text-white hover:bg-violet-500 transition-colors"
              >
                Print ({selectedCount})
              </button>
            </>
          )}

          <button
            onClick={onDailyTicket}
            className="px-3 py-1.5 rounded-lg text-sm font-medium bg-amber-700 text-amber-100 hover:bg-amber-600 transition-colors"
          >
            Daily Ticket
          </button>

          <button
            onClick={onPreview}
            className="px-3 py-1.5 rounded-lg text-sm font-medium bg-gray-800 text-gray-400 hover:bg-gray-700 transition-colors"
          >
            Preview
          </button>

          {!showArchive && (
            <button
              onClick={onPrintAll}
              className="px-3 py-1.5 rounded-lg text-sm font-medium bg-violet-600 text-white hover:bg-violet-500 transition-colors"
            >
              Print All
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
