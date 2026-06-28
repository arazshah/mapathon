"use client";
import { useState, useRef } from "react";
import MapView, { MapViewRef } from "@/components/MapView";
import QueryBox from "@/components/QueryBox";
import ResultPanel from "@/components/ResultPanel";
import FeedbackPanel from "@/components/FeedbackPanel";
import { Sparkles, Map, Info, BarChart3 } from "lucide-react";
import Link from "next/link";

export default function Home() {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<any>(null);
  const [queryId, setQueryId] = useState("");
  const mapRef = useRef<MapViewRef>(null);

  const handleSubmit = async () => {
    if (!question || loading) return;
    setLoading(true);
    setResponse(null);
    
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${apiUrl}/api/v1/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const data = await res.json();
      setResponse(data);
      setQueryId(Date.now().toString());
    } catch (error) {
      setResponse({ success: false, error: "خطا در اتصال به سرور" });
    } finally {
      setLoading(false);
    }
  };

  const handleFeatureClick = (feature: any) => {
    if (mapRef.current?.zoomToFeature) {
      mapRef.current.zoomToFeature(feature);
    }
  };

  return (
    <main className="flex h-screen w-screen overflow-hidden no-scroll bg-slate-950">
      <aside className="w-[400px] flex-shrink-0 bg-slate-900 flex flex-col border-l border-slate-800 h-full">
        <div className="p-4 border-b border-slate-800 bg-slate-900/80 backdrop-blur">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Sparkles className="text-blue-500" size={24} />
              <h1 className="text-xl font-bold text-white">مپ آتون</h1>
            </div>
            <nav className="flex gap-2">
              <Link 
                href="/about" 
                className="p-2 text-slate-400 hover:text-blue-500 transition-colors rounded-lg hover:bg-slate-800"
                title="درباره ما"
              >
                <Info size={18} />
              </Link>
              <Link 
                href="/dashboard" 
                className="p-2 text-slate-400 hover:text-blue-500 transition-colors rounded-lg hover:bg-slate-800"
                title="داشبورد"
              >
                <BarChart3 size={18} />
              </Link>
            </nav>
          </div>
        </div>

        <QueryBox 
          question={question} 
          setQuestion={setQuestion} 
          onSubmit={handleSubmit} 
          loading={loading} 
        />

        <div className="flex-1 overflow-y-auto bg-slate-950/50">
          {response ? (
            <ResultPanel 
              response={response} 
              onFeatureClick={handleFeatureClick}
            />
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-slate-600 p-4 text-center">
              <Map size={48} className="mb-4 opacity-30" />
              <p className="text-sm">سوال خود را در مورد مکان‌های تهران بپرسید</p>
              <div className="mt-6 space-y-2 text-xs text-slate-700">
                <p>💡 مثال‌ها:</p>
                <p>• فاصله میدان آزادی تا ونک چقدر است؟</p>
                <p>• داروخانه‌های نزدیک میدان ونک</p>
                <p>• مساحت پارک ملت</p>
              </div>
            </div>
          )}
        </div>

        {response?.success && (
          <FeedbackPanel 
            queryId={queryId}
            question={question}
            plan={response.debug?.plan}
            result={response.debug?.steps}
          />
        )}
      </aside>

      <section className="flex-1 h-full relative">
        <MapView 
          ref={mapRef}
          response={response} 
          onMarkerClick={handleFeatureClick}
        />
      </section>
    </main>
  );
}
