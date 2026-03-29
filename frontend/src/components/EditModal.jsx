import { useState } from 'react';

export default function EditModal({ task, onSave, onDelete, onClose }) {
  const [title, setTitle] = useState(task.title);
  const [category, setCategory] = useState(task.category);
  const [priority, setPriority] = useState(task.priority);
  const [dueDate, setDueDate] = useState(task.due_date || '');
  const [dueTime, setDueTime] = useState(task.due_time || '');
  const [notes, setNotes] = useState(task.notes || '');

  const handleSave = () => {
    const updates = {};
    if (title !== task.title) updates.title = title;
    if (category !== task.category) updates.category = category;
    if (priority !== task.priority) updates.priority = priority;
    if (dueDate !== (task.due_date || '')) updates.due_date = dueDate || null;
    if (dueTime !== (task.due_time || '')) updates.due_time = dueTime || null;
    if (notes !== (task.notes || '')) updates.notes = notes || null;

    if (Object.keys(updates).length > 0) {
      onSave(updates);
    } else {
      onClose();
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Escape') onClose();
    if (e.key === 'Enter' && e.ctrlKey) handleSave();
  };

  const inputClass =
    'w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent';

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4"
      onClick={onClose}
      onKeyDown={handleKeyDown}
    >
      <div
        className="bg-gray-900 rounded-xl border border-gray-700 p-6 w-full max-w-md shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <h2 className="text-lg font-semibold text-white mb-4">Edit Task</h2>

        <div className="space-y-3">
          <input type="text" value={title} onChange={(e) => setTitle(e.target.value)} className={inputClass} />

          <div className="grid grid-cols-2 gap-3">
            <select value={category} onChange={(e) => setCategory(e.target.value)} className={inputClass}>
              <option value="personal">Personal</option>
              <option value="work">Work</option>
              <option value="school">School</option>
            </select>
            <select value={priority} onChange={(e) => setPriority(Number(e.target.value))} className={inputClass}>
              <option value={1}>High</option>
              <option value={2}>Medium</option>
              <option value={3}>Low</option>
            </select>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <input type="date" value={dueDate} onChange={(e) => setDueDate(e.target.value)} className={inputClass} />
            <input type="time" value={dueTime} onChange={(e) => setDueTime(e.target.value)} className={inputClass} />
          </div>

          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Notes..."
            rows={3}
            className={`${inputClass} resize-none`}
          />
        </div>

        <div className="flex items-center gap-2 mt-5">
          <button
            onClick={handleSave}
            className="px-4 py-2 rounded-lg text-sm font-medium bg-indigo-600 text-white hover:bg-indigo-500 transition-colors"
          >
            Save
          </button>
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg text-sm font-medium bg-gray-800 text-gray-400 hover:bg-gray-700 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={onDelete}
            className="ml-auto px-4 py-2 rounded-lg text-sm font-medium text-red-400 hover:bg-red-500/15 transition-colors"
          >
            Delete
          </button>
        </div>

        <div className="mt-3 pt-3 border-t border-gray-800 text-xs text-gray-600 space-y-0.5">
          <div>Created: {new Date(task.created_at).toLocaleString()}</div>
          {task.printed_at && <div>Last printed: {new Date(task.printed_at).toLocaleString()}</div>}
          <div>Source: {task.source}</div>
        </div>
      </div>
    </div>
  );
}
