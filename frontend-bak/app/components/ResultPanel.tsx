"use client";

interface ResultPanelProps {
  results: any;
  onItemClick?: (item: any) => void;
}

export default function ResultPanel({ results, onItemClick }: ResultPanelProps) {
  return (
    <div className="space-y-3 animate-fade-in">
      {/* پاسخ اصلی */}
      {results.answer && (
        <div className="p-4 bg-gradient-to-l from-blue-50 to-indigo-50 border border-blue-100 rounded-2xl">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-lg">💬</span>
            <h2 className="font-bold text-slate-800 text-sm">پاسخ</h2>
          </div>
          <p className="text-slate-700 text-sm leading-relaxed">{results.answer}</p>
        </div>
      )}

      {/* لیست نتایج */}
      {results.report?.type === "list" && results.report.items?.length > 0 && (
        <div className="bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-sm">
          <div className="px-4 py-3 bg-slate-50 border-b border-slate-100 flex items-center justify-between">
            <h2 className="font-bold text-slate-700 text-sm">📍 نتایج</h2>
            <span className="text-xs bg-blue-100 text-blue-700 px-2.5 py-1 rounded-full font-semibold">
              {results.report.count} مورد
            </span>
          </div>
          <ul className="divide-y divide-slate-100 max-h-[400px] overflow-auto">
            {results.report.items.map((item: any, idx: number) => (
              <li
                key={idx}
                onClick={() => onItemClick?.(item)}
                className="px-4 py-3 hover:bg-blue-50 cursor-pointer transition group"
              >
                <div className="flex items-start gap-3">
                  <span className="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-xs font-bold group-hover:bg-blue-600 group-hover:text-white transition">
                    {idx + 1}
                  </span>
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-slate-800 text-sm truncate">
                      {item.name || "نامشخص"}
                    </p>
                    {item.type && (
                      <p className="text-xs text-slate-500 mt-0.5">{item.type}</p>
                    )}
                  </div>
                  <span className="text-slate-300 group-hover:text-blue-500 transition">←</span>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* خطا */}
      {results.error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-2xl">
          <div className="flex items-center gap-2">
            <span className="text-lg">⚠️</span>
            <div>
              <h2 className="font-bold text-red-800 text-sm">خطا</h2>
              <p className="text-red-600 text-xs mt-1">{results.error}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
