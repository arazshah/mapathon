"use client"

interface Props {
  onSubmit: (question: string) => void
  loading: boolean
}

const EXAMPLES = [
  "آزادی کجاست؟",
  "فاصله آزادی تا ونک",
  "رستوران‌های تهران",
  "بیمارستان‌های اصفهان",
]

export default function QueryBox({ onSubmit, loading }: Props) {
  return (
    <div className="w-full max-w-2xl mx-auto">
      <form
        onSubmit={(e) => {
          e.preventDefault()
          const val = (e.currentTarget.elements.namedItem("q") as HTMLInputElement).value.trim()
          if (val) onSubmit(val)
        }}
        className="flex gap-2"
      >
        <input
          name="q"
          type="text"
          placeholder="سوال جغرافیایی بپرسید... مثلاً: فاصله آزادی تا ونک"
          dir="rtl"
          className="flex-1 px-4 py-3 rounded-xl border border-gray-300 
                     focus:outline-none focus:ring-2 focus:ring-blue-500
                     text-right text-gray-800 bg-white shadow-sm"
          disabled={loading}
          autoComplete="off"
        />
        <button
          type="submit"
          disabled={loading}
          className="px-6 py-3 bg-blue-600 text-white rounded-xl
                     hover:bg-blue-700 disabled:opacity-50
                     transition-colors font-medium shadow-sm"
        >
          {loading ? "..." : "جستجو"}
        </button>
      </form>

      {/* نمونه سوال‌ها */}
      <div className="flex flex-wrap gap-2 mt-3 justify-end">
        {EXAMPLES.map((ex) => (
          <button
            key={ex}
            onClick={() => onSubmit(ex)}
            disabled={loading}
            className="text-xs px-3 py-1 rounded-full bg-gray-100 
                       text-gray-600 hover:bg-blue-50 hover:text-blue-600
                       transition-colors disabled:opacity-50"
          >
            {ex}
          </button>
        ))}
      </div>
    </div>
  )
}
