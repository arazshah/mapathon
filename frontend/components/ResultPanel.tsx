"use client"

import { useState } from "react"
import { Report } from "@/types"

interface Feature {
  properties?: Record<string, any>
  geometry?: { coordinates?: [number, number] }
}

interface Props {
  answer: string | null
  report: Report | null
  features?: Feature[]
  onSelectFeature?: (index: number, coords?: [number, number]) => void
  selectedIndex?: number | null
}

export default function ResultPanel({
  answer,
  report,
  features = [],
  onSelectFeature,
  selectedIndex,
}: Props) {
  const [currentPage, setCurrentPage] = useState(1)
  const itemsPerPage = 6

  if (!answer && !report) return null

  const listItems = report?.type === "list" ? report.items || [] : []
  const totalCount = report?.count || listItems.length
  const totalPages = Math.ceil(listItems.length / itemsPerPage)
  const startIdx = (currentPage - 1) * itemsPerPage
  const pageItems = listItems.slice(startIdx, startIdx + itemsPerPage)

  return (
    <div className="w-full h-full flex flex-col gap-3 overflow-hidden" dir="rtl">
      {/* پاسخ متنی */}
      {answer && (
        <div className="bg-gradient-to-r from-blue-50 to-blue-100 border border-blue-200 rounded-xl px-4 py-3 shadow-sm flex-shrink-0">
          <p className="text-blue-900 font-semibold text-sm leading-relaxed">{answer}</p>
        </div>
      )}

      {/* گزارش */}
      {report && (
        <div className="flex-1 overflow-y-auto min-h-0">
          {report.type === "distance" && (
            <DistanceReport report={report} />
          )}
          {report.type === "area" && (
            <AreaReport report={report} />
          )}
          {report.type === "list" && listItems.length > 0 && (
            <ListReport
              report={report}
              items={pageItems}
              totalCount={totalCount}
              currentPage={currentPage}
              totalPages={totalPages}
              onPageChange={setCurrentPage}
              onSelectItem={(idx) => {
                const globalIdx = startIdx + idx
                const feature = features[globalIdx]
                const coords = feature?.geometry?.coordinates as [number, number] | undefined
                onSelectFeature?.(globalIdx, coords)
              }}
              selectedIndex={selectedIndex}
              startIdx={startIdx}
            />
          )}
        </div>
      )}
    </div>
  )
}

function DistanceReport({ report }: { report: Report }) {
  return (
    <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm space-y-4">
      <h3 className="text-gray-600 text-xs font-bold tracking-wider">📏 جزئیات فاصله</h3>
      <div className="grid grid-cols-2 gap-2">
        <StatCard
          label="کیلومتر"
          value={report.distance_km?.toFixed(3) ?? "-"}
          icon="🌍"
          highlight
        />
        <StatCard
          label="متر"
          value={report.distance_meters?.toFixed(0) ?? "-"}
          icon="📍"
        />
      </div>
    </div>
  )
}

function AreaReport({ report }: { report: Report }) {
  return (
    <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm space-y-4">
      <h3 className="text-gray-600 text-xs font-bold tracking-wider">📐 جزئیات مساحت</h3>
      <div className="grid grid-cols-3 gap-2">
        <StatCard label="متر²" value={report.area_m2?.toFixed(0) ?? "-"} icon="📏" />
        <StatCard label="هکتار" value={report.area_hectares?.toFixed(2) ?? "-"} icon="🌾" />
        <StatCard
          label="کیلومتر²"
          value={report.area_km2?.toFixed(4) ?? "-"}
          icon="🌍"
          highlight
        />
      </div>
    </div>
  )
}

function ListReport({
  report,
  items,
  totalCount,
  currentPage,
  totalPages,
  onPageChange,
  onSelectItem,
  selectedIndex,
  startIdx,
}: {
  report: Report
  items: any[]
  totalCount: number
  currentPage: number
  totalPages: number
  onPageChange: (page: number) => void
  onSelectItem: (idx: number) => void
  selectedIndex?: number | null
  startIdx: number
}) {
  return (
    <div className="bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden flex flex-col h-full">
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-100 bg-gradient-to-r from-blue-50 to-gray-50 flex justify-between items-center flex-shrink-0">
        <h3 className="text-gray-700 font-bold text-sm">📍 نتایج</h3>
        <span className="text-xs font-semibold text-blue-600 bg-blue-100 px-2.5 py-1 rounded-full">
          {totalCount} مورد
        </span>
      </div>

      {/* Items */}
      <div className="flex-1 overflow-y-auto divide-y divide-gray-100 min-h-0">
        {items.map((item, idx) => {
          const globalIdx = startIdx + idx
          const isSelected = selectedIndex === globalIdx
          return (
            <div
              key={idx}
              onClick={() => onSelectItem(idx)}
              className={`px-4 py-3 cursor-pointer transition-all border-r-4 ${
                isSelected
                  ? "bg-red-50 border-red-500"
                  : "hover:bg-blue-50 border-transparent"
              }`}
            >
              <div className="flex justify-between items-start gap-2">
                <div className="flex-1 min-w-0">
                  <p className="text-gray-800 font-semibold text-xs leading-snug truncate">
                    {item.name || "بدون نام"}
                  </p>
                  {item.type && (
                    <p className="text-xs text-gray-400 mt-0.5">{item.type}</p>
                  )}
                </div>
                {isSelected && (
                  <span className="text-lg flex-shrink-0">✓</span>
                )}
              </div>
            </div>
          )
        })}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="px-4 py-2 border-t border-gray-100 bg-gray-50 flex justify-between items-center gap-2 flex-shrink-0">
          <button
            onClick={() => onPageChange(Math.max(1, currentPage - 1))}
            disabled={currentPage === 1}
            className="text-xs px-2.5 py-1 rounded-lg bg-white border border-gray-200 text-gray-600 hover:bg-gray-100 disabled:opacity-40 font-medium"
          >
            ← قبلی
          </button>
          <span className="text-xs text-gray-500 font-medium">
            {currentPage}/{totalPages}
          </span>
          <button
            onClick={() => onPageChange(Math.min(totalPages, currentPage + 1))}
            disabled={currentPage === totalPages}
            className="text-xs px-2.5 py-1 rounded-lg bg-white border border-gray-200 text-gray-600 hover:bg-gray-100 disabled:opacity-40 font-medium"
          >
            بعدی →
          </button>
        </div>
      )}
    </div>
  )
}

function StatCard({
  label,
  value,
  icon,
  highlight,
}: {
  label: string
  value: string
  icon: string
  highlight?: boolean
}) {
  return (
    <div
      className={`text-center p-3 rounded-lg border text-xs ${
        highlight
          ? "bg-blue-50 border-blue-200"
          : "bg-gray-50 border-gray-200"
      }`}
    >
      <div className="text-xl mb-1">{icon}</div>
      <div
        className={`font-bold text-sm ${
          highlight ? "text-blue-700" : "text-gray-700"
        }`}
      >
        {value}
      </div>
      <div className="text-xs text-gray-500 mt-0.5 font-medium">{label}</div>
    </div>
  )
}
