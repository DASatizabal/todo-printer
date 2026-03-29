export default function ReceiptPreview({ preview, onClose, onPrint }) {
  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/50" onClick={onClose}>
      <div
        className="h-full w-full max-w-md bg-gray-950 border-l border-gray-800 shadow-2xl flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-gray-800 shrink-0">
          <h2 className="text-base font-semibold text-white">Receipt Preview</h2>
          <div className="flex gap-2">
            <button
              onClick={onPrint}
              className="px-3 py-1.5 rounded-lg text-sm font-medium bg-violet-600 text-white hover:bg-violet-500 transition-colors"
            >
              Send to Printer
            </button>
            <button
              onClick={onClose}
              className="px-3 py-1.5 rounded-lg text-sm font-medium bg-gray-800 text-gray-400 hover:bg-gray-700 transition-colors"
            >
              Close
            </button>
          </div>
        </div>

        {/* Receipt paper */}
        <div className="flex-1 overflow-auto p-6 flex justify-center">
          <div
            className="w-full max-w-[340px] self-start rounded shadow-lg px-5 py-6"
            style={{
              backgroundColor: '#faf5e4',
              fontFamily: "'Courier New', Courier, monospace",
              fontSize: '11px',
              lineHeight: '1.5',
              color: '#1a1a1a',
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word',
              boxShadow: '0 4px 24px rgba(0,0,0,0.4), 2px 2px 8px rgba(0,0,0,0.2)',
            }}
          >
            {preview}
          </div>
        </div>
      </div>
    </div>
  );
}
