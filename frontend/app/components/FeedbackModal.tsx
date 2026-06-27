"use client";

import { useState } from "react";

interface FeedbackModalProps {
  queryId: string;
  question: string;
  plan: any;
  result: any;
  onClose: () => void;
}

const TYPES = [
  { key: "correct", label: "صحیح بود", icon: "✅" },
  { key: "wrong_result", label: "نتیجه اشتباه", icon: "⚠️" },
  { key: "misunderstood", label: "سوال را نفهمید", icon: "❌" },
  { key: "suggestion", label: "پیشنهاد بهبود", icon: "💡" },
];

export default function FeedbackModal({ queryId, question, plan, result, onClose }: FeedbackModalProps) {
  const [selected, setSelected] = useState<string | null>(null);
  const [comment, setComment] = useState("");
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);

  const submit = async () => {
    if (!selected) return;
    setLoading(true);
    try {
      await fetch("${API_URL}/api/v1/feedback/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query_id: queryId,
          user_question: question,
          generated_plan: plan || {},
          execution_result: result || {},
          feedback_type: selected,
          comment: comment || null,
        }),
      });
      setDone(true);
      setTimeout(onClose, 1200);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm animate-fade-in p-4">
      <div className="bg-white rounded-3xl shadow-2xl w-full max-w-md p-6">
        {done ? (
          <div className="text-center py-6">
            <div className="text-5xl mb-3">🎉</div>
            <p className="text-green-700 font-bold">سپاسگزاریم!</p>
            <p className="text-xs text-slate-500 mt-1">نظر شما ثبت شد</p>
          </div>
        ) : (
          <>
            <div className="text-center mb-5">
              <div className="text-3xl mb-2">📝</div>
              <h3 className="font-bold text-slate-800">نظر شما چیست؟</h3>
              <p className="text-xs text-slate-400 mt-1">برای ادامه، لطفاً نظرتان را ثبت کنید</p>
            </div>

            <div className="grid grid-cols-2 gap-2 mb-4">
              {TYPES.map((t) => (
                <button
                  key={t.key}
                  onClick={() => setSelected(t.key)}
                  className={`flex flex-col items-center gap-1 py-3 rounded-2xl border-2 transition ${
                    selected === t.key
                      ? "border-blue-500 bg-blue-50 text-blue-700"
                      : "border-slate-100 hover:border-slate-200 text-slate-600"
                  }`}
                >
                  <span className="text-xl">{t.icon}</span>
                  <span className="text-xs font-semibold">{t.label}</span>
                </button>
              ))}
            </div>

            <textarea
              placeholder="توضیح بیشتر (اختیاری)..."
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              className="w-full p-3 text-xs border border-slate-200 rounded-2xl focus:ring-2 focus:ring-blue-500 outline-none resize-none mb-3"
              rows={2}
            />

            <button
              onClick={submit}
              disabled={!selected || loading}
              className="w-full py-3 bg-slate-800 text-white text-sm font-semibold rounded-2xl hover:bg-slate-900 disabled:opacity-40 transition"
            >
              {loading ? "در حال ارسال..." : "ثبت و ادامه"}
            </button>
          </>
        )}
      </div>
    </div>
  );
}
