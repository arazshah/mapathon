"use client";
import { Search, Loader2 } from "lucide-react";

interface QueryBoxProps {
  question: string;
  setQuestion: (q: string) => void;
  onSubmit: () => void;
  loading: boolean;
}

export default function QueryBox({ question, setQuestion, onSubmit, loading }: QueryBoxProps) {
  const isDisabled = Boolean(loading || !question);
  
  return (
    <div className="p-4 border-b border-slate-800 bg-slate-900/50">
      <div className="relative">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && !isDisabled && onSubmit()}
          placeholder="سوال خود را بنویسید..."
          disabled={loading}
          className="w-full bg-slate-800 text-slate-100 placeholder-slate-500 rounded-lg pr-10 pl-4 py-3 border border-slate-700 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-all text-sm"
        />
        <div className="absolute right-3 top-1/2 -translate-y-1/2">
          {loading ? (
            <Loader2 size={18} className="text-blue-500 animate-spin" />
          ) : (
            <Search size={18} className="text-slate-500" />
          )}
        </div>
      </div>
      <button
        onClick={onSubmit}
        disabled={isDisabled}
        className="w-full mt-3 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-700 disabled:text-slate-500 text-white rounded-lg py-2.5 transition-all text-sm font-medium flex items-center justify-center gap-2"
      >
        {loading ? (
          <>
            <Loader2 size={16} className="animate-spin" />
            در حال جستجو...
          </>
        ) : (
          <>
            <Search size={16} />
            جستجو
          </>
        )}
      </button>
    </div>
  );
}
