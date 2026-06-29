"use client";
import { useState, useRef } from "react";
import MapView, { MapViewRef } from "@/components/MapView";
import QueryBox from "@/components/QueryBox";
import ResultPanel from "@/components/ResultPanel";
import FeedbackPanel from "@/components/FeedbackPanel";
import {
  Sparkles, Map, Info, BarChart3, ChevronRight,
  Navigation, Ruler, TreePine, Train, Coffee,
} from "lucide-react";
import Link from "next/link";

const EXAMPLES = [
  { icon: <Train size={14} />, text: "مترو نزدیک میدان انقلاب" },
  { icon: <Ruler size={14} />, text: "فاصله میدان آزادی تا ونک" },
  { icon: <Navigation size={14} />, text: "داروخانه‌های نزدیک میدان ونک" },
  { icon: <TreePine size={14} />, text: "مساحت پارک ملت" },
  { icon: <Coffee size={14} />, text: "کافه نزدیک میدان تجریش" },
];

export default function Home() {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<any>(null);
  const [queryId, setQueryId] = useState("");
  const mapRef = useRef<MapViewRef>(null);

  const handleSubmit = async (q?: string) => {
    const query = q || question;
    if (!query.trim() || loading) return;
    if (q) setQuestion(q);
    setLoading(true);
    setResponse(null);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${apiUrl}/api/v1/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: query }),
      });
      const data = await res.json();
      setResponse(data);
      setQueryId(Date.now().toString());
    } catch {
      setResponse({ success: false, error: "خطا در اتصال به سرور" });
    } finally {
      setLoading(false);
    }
  };

  const handleFeatureClick = (feature: any) => {
    mapRef.current?.zoomToFeature?.(feature);
  };

  return (
    <main className="flex h-screen w-screen overflow-hidden bg-slate-950" dir="rtl">

      {/* ======= سایدبار ======= */}
      <aside className="w-[420px] flex-shrink-0 flex flex-col bg-slate-900 border-l border-slate-800/60 h-full shadow-2xl">

        {/* هدر */}
        <header className="flex-shrink-0 px-5 py-4 border-b border-slate-800/60 bg-gradient-to-l from-slate-900 to-slate-800/50">
          <div className="flex items-center justify-between">
            {/* لوگو */}
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/20">
                <Sparkles size={18} className="text-white" />
              </div>
              <div>
                <h1 className="text-lg font-bold text-white leading-none">مپ آتون</h1>
                <p className="text-xs text-slate-500 mt-0.5">ماراتن نقشه‌های هوشمند</p>
              </div>
            </div>

            {/* ناوبری */}
            <nav className="flex items-center gap-1">
              <Link
                href="/about"
                title="درباره ما"
                className="p-2 text-slate-500 hover:text-blue-400 hover:bg-slate-800 rounded-lg transition-all"
              >
                <Info size={17} />
              </Link>
              <Link
                href="/dashboard"
                title="داشبورد مدیریت"
                className="p-2 text-slate-500 hover:text-blue-400 hover:bg-slate-800 rounded-lg transition-all"
              >
                <BarChart3 size={17} />
              </Link>
            </nav>
          </div>
        </header>

        {/* باکس جستجو */}
        <div className="flex-shrink-0 px-4 py-4 border-b border-slate-800/40">
          <QueryBox
            question={question}
            setQuestion={setQuestion}
            onSubmit={() => handleSubmit()}
            loading={loading}
          />
        </div>

        {/* محتوای اصلی */}
        <div className="flex-1 overflow-y-auto scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-transparent">
          {response ? (
            <ResultPanel response={response} onFeatureClick={handleFeatureClick} />
          ) : (
            <EmptyState onExample={handleSubmit} loading={loading} />
          )}
        </div>

        {/* فیدبک */}
        {response?.success && (
          <div className="flex-shrink-0 border-t border-slate-800/60">
            <FeedbackPanel
              queryId={queryId}
              question={question}
              plan={response.debug?.plan}
              result={response.debug?.steps}
            />
          </div>
        )}

        {/* فوتر کوچک */}
        <footer className="flex-shrink-0 px-5 py-2.5 border-t border-slate-800/40 bg-slate-950/50">
          <p className="text-xs text-slate-700 text-center">
            ساخته‌شده با ❤️ توسط{" "}
            <a
              href="https://araz.me"
              target="_blank"
              rel="noopener noreferrer"
              className="text-slate-600 hover:text-blue-400 transition-colors"
            >
              آراز شاه کرمی
            </a>
            {" "}|{" "}
            <a
              href="https://mapathon.ir"
              className="text-slate-600 hover:text-blue-400 transition-colors"
            >
              mapathon.ir
            </a>
          </p>
        </footer>
      </aside>

      {/* ======= نقشه ======= */}
      <section className="flex-1 h-full relative">
        <MapView
          ref={mapRef}
          response={response}
          onMarkerClick={handleFeatureClick}
        />

        {/* بج وضعیت روی نقشه */}
        {loading && (
          <div className="absolute top-4 left-1/2 -translate-x-1/2 z-50">
            <div className="bg-slate-900/95 backdrop-blur border border-slate-700 rounded-full px-4 py-2 flex items-center gap-2 shadow-xl">
              <span className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
              <span className="text-sm text-slate-300">در حال پردازش...</span>
            </div>
          </div>
        )}

        {/* تعداد نتایج روی نقشه */}
        {response?.success && response?.count > 0 && (
          <div className="absolute bottom-8 left-4 z-40">
            <div className="bg-slate-900/90 backdrop-blur border border-slate-700/50 rounded-xl px-4 py-2 shadow-lg">
              <p className="text-sm text-slate-300">
                <span className="text-blue-400 font-bold">{response.count}</span>
                {" "}نتیجه یافت شد
              </p>
            </div>
          </div>
        )}
      </section>
    </main>
  );
}

/* ======= کامپوننت حالت خالی ======= */
function EmptyState({
  onExample,
  loading,
}: {
  onExample: (q: string) => void;
  loading: boolean;
}) {
  return (
    <div className="flex flex-col h-full px-4 py-6">
      {/* آیکون مرکزی */}
      <div className="flex flex-col items-center justify-center flex-1 text-center pb-4">
        <div className="relative mb-5">
          <div className="w-20 h-20 bg-gradient-to-br from-blue-900/50 to-purple-900/50 rounded-3xl flex items-center justify-center border border-slate-700/50">
            <Map size={36} className="text-slate-500" />
          </div>
          <div className="absolute -top-1 -right-1 w-5 h-5 bg-blue-500 rounded-full flex items-center justify-center">
            <Sparkles size={11} className="text-white" />
          </div>
        </div>

        <h2 className="text-base font-semibold text-slate-300 mb-2">
          از تهران بپرسید
        </h2>
        <p className="text-sm text-slate-500 leading-relaxed max-w-[280px]">
          سوال مکانی خود را به فارسی بنویسید. سیستم با هوش مصنوعی پاسخ را
          روی نقشه نشان می‌دهد.
        </p>
      </div>

      {/* نمونه سوال‌ها */}
      <div className="space-y-2">
        <p className="text-xs text-slate-600 font-medium mb-3 flex items-center gap-1.5">
          <span className="w-4 h-px bg-slate-700 rounded" />
          نمونه سوال‌ها
          <span className="flex-1 h-px bg-slate-700 rounded" />
        </p>
        {EXAMPLES.map((ex, i) => (
          <button
            key={i}
            onClick={() => !loading && onExample(ex.text)}
            disabled={loading}
            className="w-full flex items-center justify-between gap-3 px-4 py-3 bg-slate-800/60 hover:bg-slate-800 border border-slate-700/50 hover:border-blue-500/40 rounded-xl transition-all group disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <div className="flex items-center gap-2.5 text-slate-400 group-hover:text-slate-200 transition-colors">
              <span className="text-blue-500/70 group-hover:text-blue-400 transition-colors">
                {ex.icon}
              </span>
              <span className="text-sm">{ex.text}</span>
            </div>
            <ChevronRight
              size={14}
              className="text-slate-600 group-hover:text-blue-400 transition-colors flex-shrink-0 rotate-180"
            />
          </button>
        ))}
      </div>

      {/* بج داده‌ها */}
      <div className="mt-4 pt-4 border-t border-slate-800/40">
        <div className="flex items-center justify-center gap-4 text-xs text-slate-700">
          <span className="flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 bg-green-500 rounded-full" />
            OpenStreetMap
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 bg-blue-500 rounded-full" />
            PostGIS
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 bg-purple-500 rounded-full" />
            GPT-4o
          </span>
        </div>
      </div>
    </div>
  );
}