import {
  DndContext,
  closestCenter,
  PointerSensor,
  KeyboardSensor,
  useSensor,
  useSensors,
} from '@dnd-kit/core';
import {
  SortableContext,
  rectSortingStrategy,
  arrayMove,
} from '@dnd-kit/sortable';
import TaskTile from './TaskTile';

export default function TaskBoard({
  tasks,
  sortBy,
  categoryFilter,
  multiSelect,
  selectedIds,
  onToggleSelect,
  onEdit,
  onArchive,
  onRestore,
  onReorder,
  showArchive,
}) {
  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 8 } }),
    useSensor(KeyboardSensor)
  );

  // DnD only when manual sort, no category filter, and viewing open tasks
  const isDraggable = sortBy === 'sort_order' && !categoryFilter && !showArchive;

  const handleDragEnd = (event) => {
    const { active, over } = event;
    if (!over || active.id === over.id) return;

    const oldIndex = tasks.findIndex((t) => t.id === active.id);
    const newIndex = tasks.findIndex((t) => t.id === over.id);
    if (oldIndex === -1 || newIndex === -1) return;

    const reordered = arrayMove(tasks, oldIndex, newIndex);
    onReorder(reordered.map((t) => t.id));
  };

  if (tasks.length === 0) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-12 text-gray-600">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="mb-3 text-gray-700">
          <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
        </svg>
        <p className="text-sm">{showArchive ? 'No archived tasks' : 'No tasks yet. Add one!'}</p>
      </div>
    );
  }

  const tileProps = (task) => ({
    key: task.id,
    task,
    isDraggable,
    multiSelect,
    selected: selectedIds.has(task.id),
    onToggleSelect: () => onToggleSelect(task.id),
    onEdit: () => onEdit(task),
    onArchive: () => onArchive(task.id),
    onRestore: () => onRestore(task.id),
    showArchive,
  });

  const gridClass = 'p-4 grid gap-3 grid-cols-1 md:grid-cols-2 xl:grid-cols-3';

  // When viewing archive, show flat list
  if (showArchive) {
    return (
      <div className={gridClass}>
        {tasks.map((task) => <TaskTile {...tileProps(task)} />)}
      </div>
    );
  }

  // Split open tasks into New (unprinted) and Printed
  const newTasks = tasks.filter((t) => !t.printed_at);
  const printedTasks = tasks.filter((t) => t.printed_at);

  const renderSection = (title, sectionTasks) => {
    if (sectionTasks.length === 0) return null;

    if (isDraggable) {
      return (
        <>
          <h2 className="px-4 pt-4 pb-1 text-lg font-bold text-gray-200">{title}</h2>
          <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
            <SortableContext items={sectionTasks.map((t) => t.id)} strategy={rectSortingStrategy}>
              <div className={gridClass}>
                {sectionTasks.map((task) => <TaskTile {...tileProps(task)} />)}
              </div>
            </SortableContext>
          </DndContext>
        </>
      );
    }

    return (
      <>
        <h2 className="px-4 pt-4 pb-1 text-lg font-bold text-gray-200">{title}</h2>
        <div className={gridClass}>
          {sectionTasks.map((task) => <TaskTile {...tileProps(task)} />)}
        </div>
      </>
    );
  };

  return (
    <div className="flex-1">
      {renderSection('New', newTasks)}
      {renderSection('Printed', printedTasks)}
    </div>
  );
}
