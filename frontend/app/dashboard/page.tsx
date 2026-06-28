"use client";
import { useState, useEffect } from "react";
import { BarChart3, ArrowLeft, Lock, TrendingUp, MessageSquare, CheckCircle, XCircle, Lightbulb } from "lucide-react";
import Link from "next/link";

export default function DashboardPage() {
  const [password, setPassword] = useState("");
  const [authed, setAuthed] = useState(false);
  const [stats, setStats] = useState<any>(null);
  const [feedbacks, setFeedbacks] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const saved = sessionStorage.getItem("dashboard_auth");
    const token = sessionStorage.getItem("dashboard_token");
    if (saved === "true" && token) {
      setAuthed(true);
      fetchData(token);
    }
  }, []);

  const handleLogin = async () => {
    setLoading(true);
    setError("");
    
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${apiUrl}/api/v1/feedback/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password }),
      });
      
      if (res.ok) {
        const data = await res.json();
        if (data.success) {
          sessionStorage.setItem("dashboard_auth", "true");
          sessionStorage.setItem("dashboard_token", data.token);
          setAuthed(true);
          fetchData(data.token);
        }
      } else {
        const errData = await res.json();
        setError(errData.detail || "رمز عبور نادرست است");
      }
    } catch (err) {
      setError("خطا در اتصال به سرور");
    } finally {
      setLoading(false);
    }
  };

  const fetchData = async (token: string) => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      
      const statsRes = await fetch(`${apiUrl}/api/v1/feedback/stats`, {
        headers: { "x-dashboard-password": token }
      });
      if (statsRes.ok) {
        setStats(await statsRes.json());
      }

      const recentRes = await fetch(`${apiUrl}/api/v1/feedback/recent?limit=20`, {
        headers: { "x-dashboard-password": token }
      });
      if (recentRes.ok) {
        const recentData = await recentRes.json();
        setFeedbacks(recentData.feedbacks || []);
      }
    } catch (err) {
      console.error("خطا در دریافت داده‌ها:", err);
    }
  };

  if (!authed) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4">
        <div className="w-full max-w-md">
          <div className="bg-slate-900 rounded-2xl p-8 border border-slate-800">
            <div className="flex items-center gap-3 mb-6">
              <Link href="/" className="text-slate-400 hover:text-white">
                <ArrowLeft size={20} />
              </Link>
              <div className="flex items-center gap-2">
                <BarChart3 className="text-blue-500" size={24} />
                <h1 className="text-xl font-bold text-white">داشبورد مپ آتون</h1>
              </div>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-slate-400 mb-2">رمز عبور</label>
                <div className="relative">
                  <Lock size={18} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500" />
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleLogin()}
                    placeholder="رمز عبور را وارد کنید"
                    className="w-full bg-slate-800 text-white rounded-lg pr-10 pl-4 py-3 border border-slate-700 focus:border-blue-500 focus:outline-none text-sm"
                  />
                </div>
              </div>

              {error && (
                <div className="bg-red-900/30 border border-red-700/50 text-red-400 rounded-lg p-3 text-sm">
                  {error}
                </div>
              )}

              <button
                onClick={handleLogin}
                disabled={loading || !password}
                className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-slate-700 text-white rounded-lg py-3 transition-all text-sm font-medium"
              >
                {loading ? "در حال ورود..." : "ورود"}
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 p-6 overflow-y-auto">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-3">
            <Link href="/" className="text-slate-400 hover:text-white">
              <ArrowLeft size={20} />
            </Link>
            <BarChart3 className="text-blue-500" size={24} />
            <h1 className="text-2xl font-bold text-white">داشبورد مپ آتون</h1>
          </div>
        </div>

        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
            <div className="bg-slate-900 rounded-xl p-6 border border-slate-800">
              <div className="flex items-center gap-2 mb-2">
                <TrendingUp className="text-blue-500" size={20} />
                <span className="text-slate-400 text-sm">کل کوئری‌ها</span>
              </div>
              <p className="text-3xl font-bold text-white">{stats.total_queries}</p>
            </div>

            <div className="bg-slate-900 rounded-xl p-6 border border-slate-800">
              <div className="flex items-center gap-2 mb-2">
                <CheckCircle className="text-green-500" size={20} />
                <span className="text-slate-400 text-sm">صحیح</span>
              </div>
              <p className="text-3xl font-bold text-green-500">{stats.correct}</p>
            </div>

            <div className="bg-slate-900 rounded-xl p-6 border border-slate-800">
              <div className="flex items-center gap-2 mb-2">
                <XCircle className="text-red-500" size={20} />
                <span className="text-slate-400 text-sm">نادرست</span>
              </div>
              <p className="text-3xl font-bold text-red-500">{stats.wrong_result}</p>
            </div>

            <div className="bg-slate-900 rounded-xl p-6 border border-slate-800">
              <div className="flex items-center gap-2 mb-2">
                <MessageSquare className="text-yellow-500" size={20} />
                <span className="text-slate-400 text-sm">اشتباه فهمیده</span>
              </div>
              <p className="text-3xl font-bold text-yellow-500">{stats.misunderstood}</p>
            </div>

            <div className="bg-slate-900 rounded-xl p-6 border border-slate-800">
              <div className="flex items-center gap-2 mb-2">
                <Lightbulb className="text-purple-500" size={20} />
                <span className="text-slate-400 text-sm">پیشنهاد</span>
              </div>
              <p className="text-3xl font-bold text-purple-500">{stats.suggestion}</p>
            </div>
          </div>
        )}

        {stats && (
          <div className="bg-slate-900 rounded-xl p-6 border border-slate-800 mb-8">
            <div className="flex items-center justify-between">
              <span className="text-slate-400">نرخ دقت سیستم</span>
              <span className="text-2xl font-bold text-blue-500">{stats.accuracy_rate}</span>
            </div>
            <div className="mt-4 bg-slate-800 rounded-full h-3 overflow-hidden">
              <div 
                className="bg-gradient-to-r from-blue-500 to-green-500 h-full rounded-full transition-all duration-500"
                style={{ width: stats.accuracy_rate }}
              />
            </div>
          </div>
        )}

        <div className="bg-slate-900 rounded-xl p-6 border border-slate-800">
          <h2 className="text-lg font-semibold text-white mb-4">آخرین نظرات</h2>
          <div className="space-y-3">
            {feedbacks.length === 0 ? (
              <p className="text-slate-500 text-center py-8">هنوز نظری ثبت نشده است</p>
            ) : (
              feedbacks.map((fb, i) => (
                <div key={i} className="bg-slate-800/50 rounded-lg p-4 border border-slate-700/50">
                  <div className="flex items-start justify-between mb-2">
                    <span className="text-sm text-slate-200">{fb.question}</span>
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      fb.feedback_type === "correct" ? "bg-green-900/50 text-green-400" :
                      fb.feedback_type === "wrong_result" ? "bg-red-900/50 text-red-400" :
                      fb.feedback_type === "misunderstood" ? "bg-yellow-900/50 text-yellow-400" :
                      "bg-purple-900/50 text-purple-400"
                    }`}>
                      {fb.feedback_type}
                    </span>
                  </div>
                  {fb.comment && (
                    <p className="text-xs text-slate-400 mt-2">{fb.comment}</p>
                  )}
                  <p className="text-xs text-slate-600 mt-2">
                    {new Date(fb.created_at).toLocaleString("fa-IR")}
                  </p>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
