import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';

const CATEGORY_BORDER = {
  work: 'border-l-blue-500',
  school: 'border-l-teal-500',
  personal: 'border-l-orange-500',
};

const PRIORITY_BADGE = {
  1: { label: 'HIGH', cls: 'bg-red-500/20 text-red-400' },
  2: { label: 'MED', cls: 'bg-amber-500/20 text-amber-400' },
  3: { label: 'LOW', cls: 'bg-gray-600/30 text-gray-400' },
};

function isOverdue(task) {
  if (!task.due_date || task.status !== 'open') return false;
  const today = new Date().toISOString().split('T')[0];
  return task.due_date < today;
}

export default function TaskTile({
  task,
  isDraggable,
  multiSelect,
  selected,
  onToggleSelect,
  onEdit,
  onArchive,
  onRestore,
  showArchive,
}) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: task.id, disabled: !isDraggable });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
    zIndex: isDragging ? 10 : undefined,
  };

  const overdue = isOverdue(task);
  const pri = PRIORITY_BADGE[task.priority] || PRIORITY_BADGE[2];

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={`
        bg-gray-800/80 rounded-lg border-l-4
        ${CATEGORY_BORDER[task.category] || 'border-l-gray-600'}
        ${overdue ? 'ring-1 ring-red-500/60' : ''}
        ${selected ? 'ring-2 ring-indigo-500' : ''}
        ${isDragging ? 'shadow-xl' : ''}
        p-3 cursor-pointer hover:bg-gray-800 transition-all
      `}
      onClick={() => (multiSelect ? onToggleSelect() : onEdit())}
    >
      <div className="flex items-start gap-2">
        {/* Checkbox for multi-select */}
        {multiSelect && (
          <input
            type="checkbox"
            checked={selected}
            onChange={onToggleSelect}
            onClick={(e) => e.stopPropagation()}
            className="mt-1 rounded border-gray-600 bg-gray-700 text-indigo-500 focus:ring-indigo-500 focus:ring-offset-0"
          />
        )}

        {/* Drag handle */}
        {isDraggable && (
          <button
            {...attributes}
            {...listeners}
            className="mt-0.5 text-gray-600 hover:text-gray-400 cursor-grab active:cursor-grabbing shrink-0 select-none"
            onClick={(e) => e.stopPropagation()}
            aria-label="Drag to reorder"
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
              <circle cx="5" cy="3" r="1.5" />
              <circle cx="11" cy="3" r="1.5" />
              <circle cx="5" cy="8" r="1.5" />
              <circle cx="11" cy="8" r="1.5" />
              <circle cx="5" cy="13" r="1.5" />
              <circle cx="11" cy="13" r="1.5" />
            </svg>
          </button>
        )}

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className={`font-medium text-sm leading-tight ${showArchive ? 'text-gray-400 line-through' : 'text-gray-100'}`}>
              {task.title}
            </span>
            <span className={`text-[10px] px-1.5 py-0.5 rounded font-semibold uppercase tracking-wide ${pri.cls}`}>
              {pri.label}
            </span>
          </div>

          <div className="flex items-center gap-2 mt-1 flex-wrap">
            {task.due_date && (
              <span className={`text-xs ${overdue ? 'text-red-400 font-semibold' : 'text-gray-500'}`}>
                {overdue ? 'OVERDUE ' : ''}
                {task.due_date}
                {task.due_time ? ` ${task.due_time}` : ''}
              </span>
            )}
            {task.source === 'lisa' && (
              <span className="text-[10px] px-1.5 py-0.5 rounded font-semibold bg-pink-500/20 text-pink-400 uppercase tracking-wide">
                From Lisa
              </span>
            )}
          </div>

          {task.notes && (
            <p className="text-xs text-gray-600 mt-1 truncate">{task.notes}</p>
          )}
        </div>

        {/* Actions */}
        <div className="shrink-0 ml-1">
          {showArchive ? (
            <button
              onClick={(e) => { e.stopPropagation(); onRestore(); }}
              className="text-xs px-2 py-1 rounded bg-emerald-500/15 text-emerald-400 hover:bg-emerald-500/25 transition-colors"
            >
              Restore
            </button>
          ) : (
            <button
              onClick={(e) => { e.stopPropagation(); onArchive(); }}
              className="text-xs px-2 py-1 rounded bg-gray-700/80 text-gray-500 hover:bg-gray-700 hover:text-gray-300 transition-colors"
              title="Mark done"
            >
              Done
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
