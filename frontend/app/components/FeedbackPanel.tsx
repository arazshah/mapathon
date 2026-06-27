"use client";

import { API_URL } from "@/app/lib/api";
import { useState } from "react";

interface FeedbackPanelProps {
  queryId: string;
  question: string;
  plan: any;
  result: any;
  onSubmit?: () => void;
}

const FEEDBACK_TYPES = [
  { key: "correct", label: "صحیح بود", icon: "✅", active: "bg-green-500 border-green-500 text-white", idle: "border-green-200 text-green-600 hover:bg-green-50" },
  { key: "wrong_result", label: "نتیجه اشتباه", icon: "⚠️", active: "bg-amber-500 border-amber-500 text-white", idle: "border-amber-200 text-amber-600 hover:bg-amber-50" },
  { key: "misunderstood", label: "سوال را نفهمید", icon: "❌", active: "bg-red-500 border-red-500 text-white", idle: "border-red-200 text-red-600 hover:bg-red-50" },
  { key: "suggestion", label: "پیشنهاد بهبود", icon: "💡", active: "bg-blue-500 border-blue-500 text-white", idle: "border-blue-200 text-blue-600 hover:bg-blue-50" },
];

export default function FeedbackPanel({ queryId, question, plan, result, onSubmit }: FeedbackPanelProps) {
  const [submitted, setSubmitted] = useState(false);
  const [comment, setComment] = useState("");
  const [selectedType, setSelectedType] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!selectedType) return;
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/v1/feedback/submit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query_id: queryId,
          user_question: question,
          generated_plan: plan || {},
          execution_result: result || {},
          feedback_type: selectedType,
          comment: comment || null,
        }),
      });
      if (response.ok) {
        setSubmitted(true);
        setTimeout(() => onSubmit?.(), 1500);
      }
    } catch (e) {
      console.error("خطا در ارسال نظر:", e);
    } finally {
      setLoading(false);
    }
  };

  if (submitted) {
    return (
      <div className="p-5 bg-gradient-to-l from-green-50 to-emerald-50 border border-green-200 rounded-2xl text-center animate-fade-in">
        <div className="text-3xl mb-2">🎉</div>
        <p className="text-green-800 font-bold text-sm">سپاسگزاریم!</p>
        <p className="text-xs text-green-600 mt-1">نظر شما به بهبود سیستم کمک می‌کند</p>
      </div>
    );
  }

  return (
    <div className="p-4 bg-white border border-slate-200 rounded-2xl shadow-sm space-y-3 animate-fade-in">
      <div className="flex items-center gap-2">
        <span className="text-lg">📝</span>
        <p className="text-sm font-bold text-slate-700">این نتیجه چطور بود؟</p>
      </div>

      <div className="grid grid-cols-2 gap-2">
        {FEEDBACK_TYPES.map((t) => (
          <button
            key={t.key}
            onClick={() => setSelectedType(t.key)}
            className={`flex items-center gap-1.5 px-3 py-2.5 text-xs font-semibold rounded-xl border-2 transition ${
              selectedType === t.key ? t.active : `bg-white ${t.idle}`
            }`}
          >
            <span>{t.icon}</span>
            {t.label}
          </button>
        ))}
      </div>

      {selectedType && (
        <div className="space-y-2 animate-fade-in">
          <textarea
            placeholder="توضیح بیشتر (اختیاری)..."
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            className="w-full p-3 text-xs border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none resize-none"
            rows={2}
          />
          <button
            onClick={handleSubmit}
            disabled={loading}
            className="w-full py-2.5 bg-slate-800 text-white text-sm font-semibold rounded-xl hover:bg-slate-900 disabled:opacity-50 transition"
          >
            {loading ? "در حال ارسال..." : "ثبت نظر"}
          </button>
        </div>
      )}
    </div>
  );
}
