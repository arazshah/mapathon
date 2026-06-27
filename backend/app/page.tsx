"use client"

import { useState, useRef } from "react"
import QueryBox from "@/components/QueryBox"
import MapView from "@/components/MapView"
import ResultPanel from "@/components/ResultPanel"
import { sendQuery } from "@/lib/api"
import { QueryResponse } from "@/types"

export default function Home() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<QueryResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [selectedFeatureIndex, setSelectedFeatureIndex] = useState<number | null>(null)
  const mapRef = useRef<any>(null)

  const handleQuery = async (question: string) => {
    setLoading(true)
    setError(null)
    setResult(null)
    setSelectedFeatureIndex(null)
    try {
      const data = await sendQuery(question)
      setResult(data)
      if (!data.success) setError(data.error || "خطای ناشناخته")
    } catch (e: any) {
      setError(e.message || "خطا در ارتباط با سرور")
    } finally {
      setLoading(false)
    }
  }

  const handleSelectResult = (index: number, coords?: [number, number]) => {
    setSelectedFeatureIndex(index)
    if (mapRef.current && coords) {
      mapRef.current.flyTo({
        center: coords,
        zoom: 15,
        duration: 1500,
      })
    }
  }

  return (
    <main className="min-h-screen bg-gradient-to-b from-blue-50 to-gray-50" dir="rtl">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-md sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-5">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-gray-400 font-medium">جستجوی هوشمند جغرافیایی</p>
            </div>
            <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-blue-700 bg-clip-text text-transparent">
              🗺️ Mapathon
            </h1>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* جعبه جستجو */}
        <div className="mb-8">
          <QueryBox onSubmit={handleQuery} loading={loading} />
        </div>

        {/* خطا */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-xl px-5 py-4 text-red-700 text-sm font-medium flex items-center gap-3">
            <span className="text-lg">⚠️</span>
            {error}
          </div>
        )}

        {/* Loading */}
        {loading && (
          <div className="flex items-center justify-center py-24 gap-3 text-gray-400">
            <div className="w-6 h-6 border-3 border-blue-500 border-t-transparent rounded-full animate-spin" />
            <span className="text-base font-medium">در حال پردازش سوال...</span>
          </div>
        )}

        {/* نقشه + نتایج (نقشه بزرگ‌تر، نتایج کوچک‌تر) */}
        {result?.success && result.map && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[700px]">
            {/* نقشه (2/3 - راست) */}
            <div className="lg:col-span-2 rounded-2xl overflow-hidden shadow-lg border border-gray-200 h-full">
              <MapView 
                data={result.map} 
                mapRef={mapRef}
                selectedIndex={selectedFeatureIndex}
              />
            </div>

            {/* نتایج (1/3 - چپ) */}
            <div className="flex flex-col gap-4 overflow-hidden">
              <ResultPanel 
                answer={result.answer} 
                report={result.report}
                features={(result.map.geojson?.features as any[]) || []}
                onSelectFeature={handleSelectResult}
                selectedIndex={selectedFeatureIndex}
              />
            </div>
          </div>
        )}

        {/* حالت خالی */}
        {!loading && !result && !error && (
          <div className="text-center py-20">
            <div className="text-8xl mb-6 opacity-30">🗺️</div>
            <h2 className="text-2xl font-bold text-gray-700 mb-2">خوش آمدید!</h2>
            <p className="text-gray-500 text-lg">سوال جغرافیایی خود را بپرسید</p>
            <p className="text-gray-400 text-sm mt-2">مثال: "داروخانه‌های تهران"، "فاصله تهران تا اصفهان"</p>
          </div>
        )}
      </div>
    </main>
  )
}
