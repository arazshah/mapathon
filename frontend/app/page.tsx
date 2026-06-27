"use client";

import { useState, useRef, useEffect } from "react";
import MapView from "./components/MapView";
import QueryBox from "./components/QueryBox";
import ResultPanel from "./components/ResultPanel";
import FeedbackModal from "./components/FeedbackModal";

export default function Home() {
  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [showFeedback, setShowFeedback] = useState(false);
  const [lastQuery, setLastQuery] = useState<any>(null);
  const mapRef = useRef<any>(null);
  const resultRef = useRef<HTMLDivElement>(null);

  // اسکرول خودکار به نتایج
  useEffect(() => {
    if (results && !loading && resultRef.current) {
      resultRef.current.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }, [results, loading]);

  const handleQuery = async (question: string) => {
    setLoading(true);
    setResults(null);
    try {
      const res = await fetch("${API_URL}/api/v1/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      if (res.ok) {
        const data = await res.json();
        setResults(data);
        setLastQuery({
          queryId: data.query_id || `query-${Date.now()}`,
          question,
          plan: data.debug?.plan,
          result: data,
        });
        if (data.map?.center && mapRef.current) {
          mapRef.current.flyTo({ center: data.map.center, zoom: data.map.zoom || 11 });
        }
        // نمایش نظرسنجی بعد از مکث کوتاه
        if (!data.error) {
          setTimeout(() => setShowFeedback(true), 1500);
        }
      } else {
        setResults({ error: "خطا در دریافت پاسخ" });
      }
    } catch {
      setResults({ error: "اتصال به سرور برقرار نشد" });
    } finally {
      setLoading(false);
    }
  };

  const handleItemClick = (item: any) => {
    if (item.lat && item.lng && mapRef.current) {
      mapRef.current.flyTo({ center: [item.lng, item.lat], zoom: 15 });
    }
  };

  return (
    <>
      <div className="flex h-screen overflow-hidden">
        {/* سایدبار (چپ) */}
        <aside className="w-[400px] flex-shrink-0 bg-white border-l border-slate-200 flex flex-col">
          <header className="px-5 py-4 border-b border-slate-100 flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center text-xl shadow-md">
                🗺️
              </div>
              <div>
                <h1 className="text-lg font-bold text-slate-800">مپ‌آتون</h1>
                <p className="text-[11px] text-slate-400">ماراتن نقشه‌های هوشمند</p>
              </div>
            </div>
<div className="flex gap-3">
  <a href="/about" className="text-xs text-slate-500 hover:text-blue-600 transition">
    ℹ️ درباره
  </a>
  <a href="/dashboard" className="text-xs text-slate-500 hover:text-blue-600 transition">
    📊 داشبورد
  </a>
</div>
          </header>

          <div className="flex-1 overflow-auto p-4">
            <QueryBox onQuery={handleQuery} loading={loading} />

            {loading && (
              <div className="flex flex-col items-center py-10 text-slate-400">
                <span className="spinner w-8 h-8 border-3 border-blue-500 border-t-transparent rounded-full" />
                <p className="text-xs mt-3">در حال جستجو...</p>
              </div>
            )}

            {results && !loading && (
              <div ref={resultRef} className="mt-4">
                <ResultPanel results={results} onItemClick={handleItemClick} />
                {lastQuery && !results.error && (
                  <button
                    onClick={() => setShowFeedback(true)}
                    className="w-full mt-3 py-2.5 text-xs text-blue-600 bg-blue-50 hover:bg-blue-100 rounded-xl font-semibold transition"
                  >
                    📝 ثبت نظر درباره این نتیجه
                  </button>
                )}
              </div>
            )}

            {!results && !loading && (
              <div className="text-center py-16 text-slate-300">
                <div className="text-5xl mb-3">🌍</div>
                <p className="text-sm text-slate-400">سوال خود را بپرسید</p>
              </div>
            )}
          </div>

          <footer className="px-5 py-3 border-t border-slate-100 text-center">
            <p className="text-[11px] text-slate-400">مپ‌آتون · ماراتن نقشه‌های هوشمند</p>
          </footer>
        </aside>

        {/* نقشه (راست) */}
        <main className="flex-1 relative">
          <MapView geojson={results?.map?.geojson} mapRef={mapRef} />
        </main>
      </div>

      {/* Modal نظرسنجی */}
      {showFeedback && lastQuery && (
        <FeedbackModal
          queryId={lastQuery.queryId}
          question={lastQuery.question}
          plan={lastQuery.plan}
          result={lastQuery.result}
          onClose={() => setShowFeedback(false)}
        />
      )}
    </>
  );
}
