import { useState } from 'react';

export default function ImportModal({ onImport, onClose }) {
  const [text, setText] = useState('');
  const [error, setError] = useState(null);
  const [importing, setImporting] = useState(false);

  const handleImport = async () => {
    setError(null);
    let tasks;

    try {
      // Strip markdown code fence if present
      let cleaned = text.trim();
      if (cleaned.startsWith('```')) {
        cleaned = cleaned.replace(/^```(?:json)?\s*\n?/, '').replace(/\n?```\s*$/, '');
      }
      tasks = JSON.parse(cleaned);
      if (!Array.isArray(tasks)) {
        tasks = [tasks];
      }
    } catch (e) {
      setError('Invalid JSON. Paste the array Claude gave you (with or without the ```json wrapper).');
      return;
    }

    if (tasks.length === 0) {
      setError('No tasks found in the JSON.');
      return;
    }

    setImporting(true);
    try {
      await onImport(tasks);
    } catch (e) {
      setError(`Import failed: ${e.message}`);
      setImporting(false);
    }
  };

  const placeholder = `Paste JSON from Claude here, e.g.:

[
  {
    "title": "Install TODO printer",
    "category": "personal",
    "priority": 1,
    "due_date": "2026-03-29",
    "due_time": "18:00",
    "notes": "30 min. Set up USB and drivers."
  },
  {
    "title": "Get milk and bread",
    "category": "personal",
    "priority": 2,
    "due_date": "2026-03-29",
    "due_time": "17:45"
  }
]`;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4"
      onClick={onClose}
    >
      <div
        className="bg-gray-900 rounded-xl border border-gray-700 p-6 w-full max-w-lg shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <h2 className="text-lg font-semibold text-white mb-1">Import Tasks</h2>
        <p className="text-sm text-gray-500 mb-4">Paste the JSON from Claude Chat</p>

        <textarea
          value={text}
          onChange={(e) => { setText(e.target.value); setError(null); }}
          placeholder={placeholder}
          rows={12}
          autoFocus
          className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-sm text-gray-100 font-mono placeholder-gray-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
        />

        {error && (
          <p className="text-sm text-red-400 mt-2">{error}</p>
        )}

        <div className="flex items-center gap-2 mt-4">
          <button
            onClick={handleImport}
            disabled={!text.trim() || importing}
            className="px-4 py-2 rounded-lg text-sm font-medium bg-indigo-600 text-white hover:bg-indigo-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {importing ? 'Importing...' : 'Import Tasks'}
          </button>
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg text-sm font-medium bg-gray-800 text-gray-400 hover:bg-gray-700 transition-colors"
          >
            Cancel
          </button>
          <span className="ml-auto text-xs text-gray-600">
            {text.trim() ? (() => {
              try {
                let c = text.trim();
                if (c.startsWith('```')) c = c.replace(/^```(?:json)?\s*\n?/, '').replace(/\n?```\s*$/, '');
                const arr = JSON.parse(c);
                const count = Array.isArray(arr) ? arr.length : 1;
                return `${count} task${count !== 1 ? 's' : ''} detected`;
              } catch { return ''; }
            })() : ''}
          </span>
        </div>
      </div>
    </div>
  );
}
