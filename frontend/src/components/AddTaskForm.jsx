import { useState } from 'react';

export default function AddTaskForm({ onSubmit, onCancel }) {
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState('personal');
  const [priority, setPriority] = useState(2);
  const [dueDate, setDueDate] = useState('');
  const [dueTime, setDueTime] = useState('');
  const [notes, setNotes] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!title.trim()) return;
    onSubmit({
      title: title.trim(),
      category,
      priority,
      due_date: dueDate || null,
      due_time: dueTime || null,
      notes: notes.trim() || null,
    });
  };

  const inputClass =
    'bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-100 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent';

  return (
    <form onSubmit={handleSubmit} className="border-b border-gray-800 p-4 bg-gray-900/50">
      <div className="grid gap-3 grid-cols-2 sm:grid-cols-4 lg:grid-cols-6">
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Task title..."
          autoFocus
          className={`col-span-2 ${inputClass}`}
        />

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

        <input type="date" value={dueDate} onChange={(e) => setDueDate(e.target.value)} className={inputClass} />
        <input type="time" value={dueTime} onChange={(e) => setDueTime(e.target.value)} className={inputClass} />

        <input
          type="text"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="Notes (optional)"
          className={`col-span-2 ${inputClass}`}
        />
      </div>

      <div className="flex gap-2 mt-3">
        <button
          type="submit"
          className="px-4 py-2 rounded-lg text-sm font-medium bg-emerald-600 text-white hover:bg-emerald-500 transition-colors"
        >
          Add Task
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 rounded-lg text-sm font-medium bg-gray-800 text-gray-400 hover:bg-gray-700 transition-colors"
        >
          Cancel
        </button>
      </div>
    </form>
  );
}
