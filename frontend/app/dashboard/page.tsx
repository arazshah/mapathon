"use client";

import { API_URL } from "@/app/lib/api";
import { useState, useEffect } from "react";

export default function Dashboard() {
  const [authenticated, setAuthenticated] = useState(false);
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [stats, setStats] = useState<any>(null);
  const [recent, setRecent] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  // بررسی توکن ذخیره‌شده
  useEffect(() => {
    const saved = sessionStorage.getItem("dashboard_token");
    if (saved) {
      setPassword(saved);
      loadData(saved);
    }
  }, []);

  const loadData = async (pass: string) => {
    setLoading(true);
    try {
      const [s, r] = await Promise.all([
        fetch(`${API_URL}/api/v1/feedback/stats`, {
          headers: { "x-dashboard-password": pass },
        }),
        fetch(`${API_URL}/api/v1/feedback/recent`, {
          headers: { "x-dashboard-password": pass },
        }),
      ]);
      if (s.status === 401) {
        setError("رمز عبور نادرست است");
        sessionStorage.removeItem("dashboard_token");
        setAuthenticated(false);
        return;
      }
      const statsData = await s.json();
      const recentData = await r.json();
      setStats(statsData);
      setRecent(recentData.feedbacks || []);
      setAuthenticated(true);
      sessionStorage.setItem("dashboard_token", pass);
      setError("");
    } catch {
      setError("اتصال به سرور برقرار نشد");
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    if (password.trim()) loadData(password);
  };

  const logout = () => {
    sessionStorage.removeItem("dashboard_token");
    setAuthenticated(false);
    setPassword("");
    setStats(null);
    setRecent([]);
  };

  const TYPE_LABELS: Record<string, { label: string; color: string }> = {
    correct: { label: "✅ صحیح", color: "bg-green-100 text-green-700" },
    wrong_result: { label: "⚠️ اشتباه", color: "bg-amber-100 text-amber-700" },
    misunderstood: { label: "❌ نفهمید", color: "bg-red-100 text-red-700" },
    suggestion: { label: "💡 پیشنهاد", color: "bg-blue-100 text-blue-700" },
  };

  // صفحه ورود
  if (!authenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 p-4">
        <form
          onSubmit={handleLogin}
          className="bg-white rounded-3xl shadow-xl p-8 w-full max-w-sm"
        >
          <div className="text-center mb-6">
            <div className="text-4xl mb-2">🔒</div>
            <h1 className="text-xl font-bold text-slate-800">ورود به داشبورد</h1>
            <p className="text-xs text-slate-400 mt-1">رمز عبور را وارد کنید</p>
          </div>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="رمز عبور"
            className="w-full p-3 border border-slate-200 rounded-2xl text-center focus:ring-2 focus:ring-blue-500 outline-none mb-3"
          />
          {error && <p className="text-red-500 text-xs text-center mb-3">{error}</p>}
          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-slate-800 text-white font-semibold rounded-2xl hover:bg-slate-900 disabled:opacity-50 transition"
          >
            {loading ? "در حال بررسی..." : "ورود"}
          </button>
          <a href="/" className="block text-center text-xs text-slate-400 hover:text-blue-600 mt-4">
            ← بازگشت به سایت
          </a>
        </form>
      </div>
    );
  }

  // داشبورد
  return (
    <div className="min-h-screen bg-slate-50 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold text-slate-800">📊 داشبورد نظرات</h1>
          <div className="flex gap-3">
            <button onClick={logout} className="text-sm text-red-500 hover:underline">
              خروج
            </button>
            <a href="/" className="text-sm text-blue-600 hover:underline">
              ← بازگشت
            </a>
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-6">
          <StatCard label="کل نظرات" value={stats?.total_queries} color="from-slate-600 to-slate-700" />
          <StatCard label="صحیح" value={stats?.correct} color="from-green-500 to-green-600" />
          <StatCard label="اشتباه" value={stats?.wrong_result} color="from-amber-500 to-amber-600" />
          <StatCard label="نفهمید" value={stats?.misunderstood} color="from-red-500 to-red-600" />
          <StatCard label="دقت" value={stats?.accuracy_rate} color="from-blue-500 to-blue-600" />
        </div>

        <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden">
          <div className="px-5 py-3 border-b border-slate-100">
            <h2 className="font-bold text-slate-700">آخرین نظرات</h2>
          </div>
          {recent.length === 0 ? (
            <p className="text-center text-slate-400 py-10 text-sm">هنوز نظری ثبت نشده</p>
          ) : (
            <ul className="divide-y divide-slate-100">
              {recent.map((f, i) => {
                const t = TYPE_LABELS[f.feedback_type] || { label: f.feedback_type, color: "bg-slate-100" };
                return (
                  <li key={i} className="px-5 py-3">
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-semibold text-slate-800 truncate">{f.question}</p>
                        {f.comment && <p className="text-xs text-slate-500 mt-1">💬 {f.comment}</p>}
                        <p className="text-[11px] text-slate-300 mt-1">
                          {new Date(f.created_at).toLocaleString("fa-IR")}
                        </p>
                      </div>
                      <span className={`text-xs px-2.5 py-1 rounded-full font-semibold ${t.color}`}>
                        {t.label}
                      </span>
                    </div>
                  </li>
                );
              })}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}

function StatCard({ label, value, color }: { label: string; value: any; color: string }) {
  return (
    <div className={`bg-gradient-to-br ${color} rounded-2xl p-4 text-white shadow-md`}>
      <p className="text-2xl font-bold">{value ?? 0}</p>
      <p className="text-xs opacity-80 mt-1">{label}</p>
    </div>
  );
}
