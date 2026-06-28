'use client';

import { useState } from 'react';

type FeedbackType = 'correct' | 'wrong_result' | 'misunderstood' | 'suggestion';

const labels: Record<FeedbackType, string> = {
  correct: '✅ درست بود',
  wrong_result: '❌ نتیجه نادرست',
  misunderstood: '🤔 سؤال را بد فهمید',
  suggestion: '💡 پیشنهاد دارم',
};

const colors: Record<FeedbackType, string> = {
  correct: 'bg-green-50 text-green-700 border-green-200',
  wrong_result: 'bg-red-50 text-red-700 border-red-200',
  misunderstood: 'bg-yellow-50 text-yellow-700 border-yellow-200',
  suggestion: 'bg-blue-50 text-blue-700 border-blue-200',
};

interface FeedbackPanelProps {
  isOpen: boolean;
  onClose: () => void;
  query: string;
  result: any;
}

export default function FeedbackPanel({ isOpen, onClose, query, result }: FeedbackPanelProps) {
  const [type, setType] = useState<FeedbackType | null>(null);
  const [comment, setComment] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [sent, setSent] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!type) return;

    setSubmitting(true);
    try {
      await fetch('/api/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query,
          feedback_type: type,
          comment,
          result_summary: result ? JSON.stringify(result).slice(0, 500) : '',
        }),
      });
      setSent(true);
      setTimeout(() => {
        setSent(false);
        setType(null);
        setComment('');
        onClose();
      }, 2000);
    } catch (error) {
      console.error('Feedback submit error:', error);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed z-40 md:bottom-6 md:right-6 md:left-auto md:top-auto bottom-4 left-4 right-4 top-auto" dir="rtl">
      <div className="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-5 shadow-2xl">
        <div className="mb-4 flex items-center justify-between">
          <h3 className="font-semibold text-slate-800">بازخورد شما</h3>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 text-xl">
            ✕
          </button>
        </div>

        {sent ? (
          <div className="text-center py-6">
            <p className="text-lg font-semibold text-green-600">🙏 ممنون از شما</p>
            <p className="text-sm text-slate-500 mt-2">بازخورد ثبت شد و به بهبود سامانه کمک می‌کند.</p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <p className="text-sm text-slate-600">
              لطفاً پس از مشاهده نتیجه، نظر خود را ثبت کنید:
            </p>

            <div className="grid grid-cols-2 gap-2">
              {(Object.keys(labels) as FeedbackType[]).map((t) => (
                <button
                  key={t}
                  type="button"
                  onClick={() => setType(t)}
                  className={`rounded-lg border px-3 py-2 text-sm transition ${
                    type === t
                      ? `${colors[t]} ring-2 ring-offset-1`
                      : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-50'
                  }`}
                >
                  {labels[t]}
                </button>
              ))}
            </div>

            <textarea
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              placeholder="توضیح اختیاری... مثلاً این نتیجه چه مشکلی دارد؟"
              className="w-full rounded-lg border border-slate-200 p-3 text-sm focus:border-green-500 focus:outline-none resize-none"
              rows={3}
            />

            <div className="flex gap-2">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 rounded-lg bg-slate-100 px-4 py-2 text-sm text-slate-700 hover:bg-slate-200"
              >
                بعداً
              </button>
              <button
                type="submit"
                disabled={!type || submitting}
                className="flex-1 rounded-lg bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700 disabled:opacity-50"
              >
                {submitting ? 'در حال ثبت...' : 'ثبت نظر'}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
