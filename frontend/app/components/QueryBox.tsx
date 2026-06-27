"use client";

import { useState } from "react";

interface QueryBoxProps {
  onQuery: (question: string) => void;
  loading: boolean;
}

const SUGGESTIONS = [
  "فاصله آزادی تا ونک",
  "رستوران‌های تهران",
  "بیمارستان‌های تهران",
  "داروخانه‌های نزدیک میدان ونک",
  "مساحت پارک ملت",
  "نزدیک‌ترین مترو به برج میلاد",
];

export default function QueryBox({ onQuery, loading }: QueryBoxProps) {
  const [question, setQuestion] = useState("");

  const isDisabled: boolean = Boolean(loading) || question.trim().length === 0;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!isDisabled) onQuery(question);
  };

  return (
    <div className="space-y-3">
      {/* نوتیس تهران */}
      <div className="flex items-center gap-2 text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded-xl px-3 py-2">
        <span>🏙️</span>
        <span>در حال حاضر فقط داده‌های شهر <strong>تهران</strong> موجود است</span>
      </div>

      <form onSubmit={handleSubmit}>
        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              handleSubmit(e as unknown as React.FormEvent);
            }
          }}
          placeholder="مثلاً: فاصله آزادی تا ونک چقدر است؟"
          className="w-full p-4 text-sm border border-slate-200 rounded-2xl focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none resize-none shadow-sm transition"
          rows={3}
          disabled={Boolean(loading)}
        />
        <button
          type="submit"
          disabled={isDisabled}
          className="w-full mt-2 py-3 bg-gradient-to-l from-blue-600 to-blue-500 text-white rounded-2xl font-semibold hover:from-blue-700 hover:to-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition shadow-md flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <span className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full inline-block" />
              در حال پردازش...
            </>
          ) : (
            <>🔍 جستجو</>
          )}
        </button>
      </form>

      <div className="space-y-1">
        <p className="text-xs text-slate-400 pr-1">نمونه سوال‌ها:</p>
        <div className="flex flex-wrap gap-2">
          {SUGGESTIONS.map((s) => (
            <button
              key={s}
              type="button"
              onClick={() => {
                setQuestion(s);
                onQuery(s);
              }}
              disabled={Boolean(loading)}
              className="text-xs px-3 py-1.5 bg-slate-100 hover:bg-blue-50 hover:text-blue-600 text-slate-600 rounded-full transition border border-slate-200 disabled:opacity-50"
            >
              {s}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
