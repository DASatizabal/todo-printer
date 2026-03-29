import { useState, useEffect, useCallback } from 'react';
import * as api from './api';
import StatsBar from './components/StatsBar';
import FilterBar from './components/FilterBar';
import TaskBoard from './components/TaskBoard';
import AddTaskForm from './components/AddTaskForm';
import EditModal from './components/EditModal';
import ReceiptPreview from './components/ReceiptPreview';

export default function App() {
  const [tasks, setTasks] = useState([]);
  const [stats, setStats] = useState(null);
  const [filter, setFilter] = useState({ category: null, sortBy: 'sort_order' });
  const [showArchive, setShowArchive] = useState(false);
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingTask, setEditingTask] = useState(null);
  const [multiSelect, setMultiSelect] = useState(false);
  const [selectedIds, setSelectedIds] = useState(new Set());
  const [receiptPreview, setReceiptPreview] = useState(null);
  const [loading, setLoading] = useState(true);
  const [syncPending, setSyncPending] = useState(0);
  const [syncing, setSyncing] = useState(false);

  // --------------------------------------------------
  // Data loading
  // --------------------------------------------------
  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      const status = showArchive ? 'archived' : 'open';
      const [tasksData, statsData, pendingData] = await Promise.all([
        api.listTasks(status, filter.category, filter.sortBy),
        api.getStats(),
        api.getSyncPending().catch(() => ({ pending: 0 })),
      ]);
      setTasks(tasksData);
      setStats(statsData);
      setSyncPending(pendingData.pending);
    } catch (err) {
      console.error('Failed to load data:', err);
    } finally {
      setLoading(false);
    }
  }, [showArchive, filter.category, filter.sortBy]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // --------------------------------------------------
  // Task actions
  // --------------------------------------------------
  const handleCreateTask = async (data) => {
    await api.createTask(data);
    setShowAddForm(false);
    loadData();
  };

  const handleUpdateTask = async (id, data) => {
    await api.updateTask(id, data);
    setEditingTask(null);
    loadData();
  };

  const handleArchiveTask = async (id) => {
    await api.archiveTask(id);
    selectedIds.delete(id);
    setSelectedIds(new Set(selectedIds));
    loadData();
  };

  const handleRestoreTask = async (id) => {
    await api.restoreTask(id);
    loadData();
  };

  const handleDeleteTask = async (id) => {
    await api.deleteTask(id);
    setEditingTask(null);
    loadData();
  };

  const handleReorder = async (orderedIds) => {
    // Optimistic: reorder local state immediately
    const taskMap = Object.fromEntries(tasks.map((t) => [t.id, t]));
    setTasks(orderedIds.map((id) => taskMap[id]).filter(Boolean));

    await api.reorderTasks(orderedIds);
  };

  // --------------------------------------------------
  // Selection
  // --------------------------------------------------
  const handleToggleSelect = (id) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const handleBulkArchive = async () => {
    await Promise.all([...selectedIds].map(api.archiveTask));
    setSelectedIds(new Set());
    setMultiSelect(false);
    loadData();
  };

  // --------------------------------------------------
  // Printing
  // --------------------------------------------------
  const buildPrintOptions = () => {
    if (multiSelect && selectedIds.size > 0) {
      return { task_ids: [...selectedIds] };
    }
    if (filter.category) {
      return { category: filter.category };
    }
    return { all_open: true };
  };

  const handlePreview = async () => {
    const options = buildPrintOptions();
    const result = await api.previewPrint(options);
    setReceiptPreview({ text: result.preview, options });
  };

  const handlePrintAll = async () => {
    await api.printTasks({ all_open: true });
    loadData();
  };

  const handlePrintSelected = async () => {
    if (selectedIds.size === 0) return;
    await api.printTasks({ task_ids: [...selectedIds] });
    loadData();
  };

  const handlePrintFromPreview = async () => {
    if (!receiptPreview) return;
    if (receiptPreview.options) {
      await api.printTasks(receiptPreview.options);
    } else {
      await api.printDailyTicket();
    }
    setReceiptPreview(null);
    loadData();
  };

  const handleDailyTicket = async () => {
    const result = await api.previewDailyTicket();
    setReceiptPreview({ text: result.preview, options: null });
  };

  const handleSync = async () => {
    setSyncing(true);
    try {
      await api.syncRemoteTasks();
      loadData();
    } catch (err) {
      console.error('Sync failed:', err);
    } finally {
      setSyncing(false);
    }
  };

  // --------------------------------------------------
  // Render
  // --------------------------------------------------
  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 flex flex-col">
      {/* Header */}
      <header className="flex items-center justify-between px-4 py-3 border-b border-gray-800">
        <h1 className="text-lg font-bold tracking-tight">
          <span className="text-gray-400">todo</span>
          <span className="text-violet-400">printer</span>
        </h1>
        <span className="text-xs text-gray-600 hidden sm:inline">
          receipt-powered productivity
        </span>
      </header>

      <StatsBar stats={stats} />

      <FilterBar
        filter={filter}
        onCategoryChange={(cat) => setFilter((f) => ({ ...f, category: cat }))}
        onSortChange={(sort) => setFilter((f) => ({ ...f, sortBy: sort }))}
        showArchive={showArchive}
        onToggleArchive={() => {
          setShowArchive((v) => !v);
          setSelectedIds(new Set());
          setMultiSelect(false);
        }}
        multiSelect={multiSelect}
        onToggleMultiSelect={() => {
          setMultiSelect((v) => !v);
          setSelectedIds(new Set());
        }}
        selectedCount={selectedIds.size}
        onAddClick={() => setShowAddForm(true)}
        onSync={handleSync}
        syncPending={syncPending}
        syncing={syncing}
        onDailyTicket={handleDailyTicket}
        onPreview={handlePreview}
        onPrintAll={handlePrintAll}
        onPrintSelected={handlePrintSelected}
        onBulkArchive={handleBulkArchive}
      />

      {showAddForm && (
        <AddTaskForm onSubmit={handleCreateTask} onCancel={() => setShowAddForm(false)} />
      )}

      {/* Loading / Task board */}
      {loading && tasks.length === 0 ? (
        <div className="flex-1 flex items-center justify-center text-gray-600">
          <div className="animate-pulse text-sm">Loading tasks...</div>
        </div>
      ) : (
        <TaskBoard
          tasks={tasks}
          sortBy={filter.sortBy}
          categoryFilter={filter.category}
          multiSelect={multiSelect}
          selectedIds={selectedIds}
          onToggleSelect={handleToggleSelect}
          onEdit={setEditingTask}
          onArchive={handleArchiveTask}
          onRestore={handleRestoreTask}
          onReorder={handleReorder}
          showArchive={showArchive}
        />
      )}

      {/* Edit modal */}
      {editingTask && (
        <EditModal
          task={editingTask}
          onSave={(data) => handleUpdateTask(editingTask.id, data)}
          onDelete={() => handleDeleteTask(editingTask.id)}
          onClose={() => setEditingTask(null)}
        />
      )}

      {/* Receipt preview panel */}
      {receiptPreview && (
        <ReceiptPreview
          preview={receiptPreview.text}
          onClose={() => setReceiptPreview(null)}
          onPrint={handlePrintFromPreview}
        />
      )}
    </div>
  );
}
