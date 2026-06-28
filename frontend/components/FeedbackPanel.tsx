"use client";
import { useState } from "react";
import { CheckCircle, XCircle, MessageSquare, Lightbulb, Loader2 } from "lucide-react";

interface FeedbackPanelProps {
  queryId: string;
  question: string;
  plan?: any;
  result?: any;
}

export default function FeedbackPanel({ queryId, question, plan, result }: FeedbackPanelProps) {
  const [selectedType, setSelectedType] = useState<string>("");
  const [comment, setComment] = useState("");
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async () => {
    if (!selectedType) return;
    setLoading(true);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      await fetch(`${apiUrl}/api/v1/feedback/submit`, {
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
      setSubmitted(true);
    } catch (err) {
      console.error("خطا در ارسال نظر:", err);
    } finally {
      setLoading(false);
    }
  };

  if (submitted) {
    return (
      <div className="p-4 border-t border-slate-800 bg-green-900/20">
        <div className="flex items-center gap-2 text-green-400">
          <CheckCircle size={20} />
          <p className="text-sm">تشکر از نظر شما!</p>
        </div>
      </div>
    );
  }

  const feedbackTypes = [
    { id: "correct", label: "صحیح", icon: CheckCircle, color: "green" },
    { id: "wrong_result", label: "نادرست", icon: XCircle, color: "red" },
    { id: "misunderstood", label: "اشتباه فهمیده", icon: MessageSquare, color: "yellow" },
    { id: "suggestion", label: "پیشنهاد", icon: Lightbulb, color: "purple" },
  ];

  return (
    <div className="p-4 border-t border-slate-800 bg-slate-900/80">
      <p className="text-sm text-slate-400 mb-3">نظر شما درباره این نتیجه؟</p>
      
      <div className="grid grid-cols-2 gap-2 mb-3">
        {feedbackTypes.map((type) => {
          const Icon = type.icon;
          return (
            <button
              key={type.id}
              onClick={() => setSelectedType(type.id)}
              className={`flex items-center gap-2 p-2 rounded-lg border transition-all text-xs ${
                selectedType === type.id
                  ? `bg-${type.color}-900/50 border-${type.color}-500 text-${type.color}-400`
                  : "bg-slate-800 border-slate-700 text-slate-400 hover:bg-slate-700"
              }`}
            >
              <Icon size={14} />
              {type.label}
            </button>
          );
        })}
      </div>

      <textarea
        value={comment}
        onChange={(e) => setComment(e.target.value)}
        placeholder="توضیحات بیشتر (اختیاری)..."
        className="w-full bg-slate-800 text-slate-100 placeholder-slate-500 rounded-lg p-2 border border-slate-700 focus:border-blue-500 focus:outline-none text-xs mb-2 resize-none"
        rows={2}
      />

      <button
        onClick={handleSubmit}
        disabled={loading || !selectedType}
        className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-slate-700 text-white rounded-lg py-2 transition-all text-xs font-medium flex items-center justify-center gap-2"
      >
        {loading ? (
          <>
            <Loader2 size={14} className="animate-spin" />
            در حال ارسال...
          </>
        ) : (
          "ارسال نظر"
        )}
      </button>
    </div>
  );
}
