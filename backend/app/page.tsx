'use client';

import { useState, useEffect } from 'react';
import MapView from './components/MapView';
import QueryBox from './components/QueryBox';
import ResultPanel from './components/ResultPanel';
import FeedbackPanel from './components/FeedbackPanel';

export default function Home() {
  const [query, setQuery] = useState('');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [feedbackOpen, setFeedbackOpen] = useState(false);
  const [feedbackReady, setFeedbackReady] = useState(false);

  const handleSearch = async (q: string) => {
    setQuery(q);
    setFeedbackOpen(false);
    setFeedbackReady(false);
    setLoading(true);
    setResult(null);

    try {
      const res = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: q }),
      });
      const data = await res.json();
      setResult(data);
      setFeedbackReady(true);
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen w-full overflow-hidden bg-slate-50" dir="rtl">
      <aside className="w-[32%] min-w-[320px] h-full overflow-y-auto border-l border-slate-200 bg-white p-4 shadow-sm flex flex-col">
        <QueryBox onSearch={handleSearch} loading={loading} />
        <div className="flex-1">
          <ResultPanel result={result} loading={loading} />
        </div>
      </aside>

      <main className="relative flex-1 h-full">
        <MapView result={result} />

        {feedbackReady && !feedbackOpen && (
          <button
            onClick={() => setFeedbackOpen(true)}
            className="absolute bottom-6 right-6 z-30 flex items-center gap-2 rounded-full bg-green-600 px-4 py-3 text-sm font-semibold text-white shadow-xl hover:bg-green-700 transition hover:scale-105"
            aria-label="ثبت نظر"
          >
            <span>📝</span>
            <span>ثبت نظر</span>
          </button>
        )}

        <FeedbackPanel
          isOpen={feedbackOpen}
          onClose={() => setFeedbackOpen(false)}
          query={query}
          result={result}
        />
      </main>
    </div>
  );
}
