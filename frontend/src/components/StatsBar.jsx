export default function StatsBar({ stats }) {
  if (!stats) return null;

  return (
    <div className="flex flex-wrap items-center gap-x-5 gap-y-1 px-4 py-2.5 bg-gray-900/60 border-b border-gray-800 text-sm">
      <div className="flex items-center gap-1.5">
        <span className="text-gray-500">Open</span>
        <span className="font-semibold text-white">{stats.total_open}</span>
      </div>

      {stats.overdue_count > 0 && (
        <div className="flex items-center gap-1.5">
          <span className="text-red-500">Overdue</span>
          <span className="font-semibold text-red-400">{stats.overdue_count}</span>
        </div>
      )}

      <div className="flex items-center gap-1.5">
        <span className="text-gray-500">Archived</span>
        <span className="text-gray-400">{stats.total_archived}</span>
      </div>

      <div className="flex items-center gap-2 ml-auto">
        {(stats.by_category.work ?? 0) > 0 && (
          <span className="px-2 py-0.5 rounded text-xs font-medium bg-blue-500/15 text-blue-400">
            Work {stats.by_category.work}
          </span>
        )}
        {(stats.by_category.school ?? 0) > 0 && (
          <span className="px-2 py-0.5 rounded text-xs font-medium bg-teal-500/15 text-teal-400">
            School {stats.by_category.school}
          </span>
        )}
        {(stats.by_category.personal ?? 0) > 0 && (
          <span className="px-2 py-0.5 rounded text-xs font-medium bg-orange-500/15 text-orange-400">
            Personal {stats.by_category.personal}
          </span>
        )}
      </div>
    </div>
  );
}
