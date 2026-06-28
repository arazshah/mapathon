"use client";
import { Sparkles, Target, Users, Code, ArrowLeft, Mail, Map } from "lucide-react";
import Link from "next/link";

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-200 overflow-y-auto">
      <div className="max-w-4xl mx-auto px-6 py-12">
        {/* هدر */}
        <div className="flex items-center gap-4 mb-12">
          <Link href="/" className="text-slate-400 hover:text-white">
            <ArrowLeft size={24} />
          </Link>
          <div className="flex items-center gap-2">
            <Sparkles className="text-blue-500" size={28} />
            <h1 className="text-3xl font-bold text-white">درباره مپ آتون</h1>
          </div>
        </div>

        {/* معرفی */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold text-blue-400 mb-4">سامانه چیست؟</h2>
          <p className="text-slate-300 leading-relaxed mb-4">
            مپ آتون (Mapathon) یک سامانه هوشمند جستجو و تحلیل مکانی است که با استفاده از 
            هوش مصنوعی و داده‌های OpenStreetMap، به سوالات مکانی کاربران به زبان طبیعی پاسخ می‌دهد.
          </p>
          <p className="text-slate-300 leading-relaxed">
            این سامانه قادر است فاصله بین مکان‌ها، مکان‌های نزدیک، مساحت مناطق و اطلاعات 
            جغرافیایی مختلف را به صورت خودکار محاسبه و نمایش دهد.
          </p>
        </section>

        {/* ویژگی‌ها */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold text-blue-400 mb-4">ویژگی‌ها</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-slate-900 rounded-xl p-6 border border-slate-800">
              <Map className="text-blue-500 mb-3" size={24} />
              <h3 className="text-lg font-semibold text-white mb-2">جستجوی هوشمند</h3>
              <p className="text-sm text-slate-400">
                پرسیدن سوال به زبان طبیعی و دریافت پاسخ دقیق
              </p>
            </div>
            <div className="bg-slate-900 rounded-xl p-6 border border-slate-800">
              <Target className="text-green-500 mb-3" size={24} />
              <h3 className="text-lg font-semibold text-white mb-2">تحلیل مکانی</h3>
              <p className="text-sm text-slate-400">
                محاسبه فاصله، مساحت و یافتن مکان‌های نزدیک
              </p>
            </div>
          </div>
        </section>

        {/* هدف */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold text-blue-400 mb-4">هدف پروژه</h2>
          <p className="text-slate-300 leading-relaxed">
            هدف ما ایجاد یک سامانه هوشمند برای پاسخگویی به سوالات مکانی کاربران به زبان فارسی 
            و بهبود دسترسی به اطلاعات جغرافیایی است.
          </p>
        </section>

        {/* تیم */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold text-blue-400 mb-4">تیم توسعه</h2>
          <div className="bg-slate-900 rounded-xl p-6 border border-slate-800">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
                <Users className="text-white" size={28} />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white">آراز شاه کرمی</h3>
                <p className="text-sm text-slate-400">برنامه‌نویس و توسعه‌دهنده اصلی</p>
              </div>
            </div>
          </div>
        </section>

        {/* تماس */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold text-blue-400 mb-4">تماس با ما</h2>
          <div className="bg-slate-900 rounded-xl p-6 border border-slate-800">
            <div className="flex items-center gap-3 mb-3">
              <Mail className="text-blue-500" size={20} />
              <a href="mailto:info@mapathon.ir" className="text-slate-300 hover:text-blue-400">
                info@mapathon.ir
              </a>
            </div>
            <div className="flex items-center gap-3">
              <Code className="text-blue-500" size={20} />
              <a href="https://mapathon.ir" className="text-slate-300 hover:text-blue-400">
                mapathon.ir
              </a>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
