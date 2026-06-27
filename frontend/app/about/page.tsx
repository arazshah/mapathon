"use client";

export default function About() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white">
      {/* هدر */}
      <header className="px-6 py-4 bg-white border-b border-slate-100">
        <div className="max-w-3xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center text-xl shadow-md">
              🗺️
            </div>
            <h1 className="text-lg font-bold text-slate-800">مپ‌آتون</h1>
          </div>
          <a href="/" className="text-sm text-blue-600 hover:underline">
            ← بازگشت
          </a>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-6 py-10 space-y-8">
        {/* عنوان */}
        <section className="text-center">
          <div className="text-5xl mb-4">🗺️</div>
          <h1 className="text-3xl font-bold text-slate-800 mb-2">
            مپ‌آتون
          </h1>
          <p className="text-slate-500">ماراتن نقشه‌های هوشمند</p>
        </section>

        {/* چیست */}
        <section className="bg-white rounded-3xl p-7 border border-slate-100 shadow-sm">
          <h2 className="text-lg font-bold text-slate-800 mb-3 flex items-center gap-2">
            <span>💡</span> مپ‌آتون چیست؟
          </h2>
          <p className="text-slate-600 leading-relaxed text-sm">
            مپ‌آتون یک سامانهٔ هوشمند پرس‌وجوی جغرافیایی برای ایران است که به شما
            امکان می‌دهد سوالات مکانی خود را به زبان طبیعی فارسی یا انگلیسی بپرسید
            و پاسخ دقیق دریافت کنید — بدون نیاز به دانش GIS، SQL یا برنامه‌نویسی.
          </p>
          <p className="text-slate-600 leading-relaxed text-sm mt-3">
            می‌توانید سوالاتی مانند «فاصله تهران تا اصفهان»، «رستوران‌های نزدیک
            میدان آزادی» یا «بیمارستان‌های اصفهان» را بپرسید و سامانه به‌صورت
            خودکار آن را به یک پلن اجرایی تبدیل کرده، روی داده‌های OpenStreetMap
            اجرا و نتیجه را روی نقشه نمایش می‌دهد.
          </p>
        </section>

        {/* چرا */}
        <section className="bg-white rounded-3xl p-7 border border-slate-100 shadow-sm">
          <h2 className="text-lg font-bold text-slate-800 mb-3 flex items-center gap-2">
            <span>🎯</span> چرا این پروژه؟
          </h2>
          <p className="text-slate-600 leading-relaxed text-sm">
            داده‌های مکانی ارزشمندی مثل OpenStreetMap برای ایران موجود است، اما
            استفاده از آن‌ها نیازمند دانش تخصصی GIS و SQL است که مانع بزرگی برای
            کاربران عادی، پژوهشگران و کسب‌وکارهای کوچک محسوب می‌شود.
          </p>
          <p className="text-slate-600 leading-relaxed text-sm mt-3">
            هدف مپ‌آتون این است که با کمک هوش مصنوعی، این شکاف را پر کند و تحلیل‌های
            مکانی را برای <strong>همه</strong> در دسترس کند — فقط کافیست به زبان
            خودتان سوال بپرسید.
          </p>
        </section>

        {/* درباره سازنده */}
        <section className="bg-white rounded-3xl p-7 border border-slate-100 shadow-sm">
          <h2 className="text-lg font-bold text-slate-800 mb-3 flex items-center gap-2">
            <span>👨‍💻</span> دربارهٔ سازنده
          </h2>
          <p className="text-slate-600 leading-relaxed text-sm">
            این پروژه توسط <strong>آراز شاه‌کرمی</strong>، مهندس هوش مصنوعی مکانی و
            توسعه‌دهندهٔ بک‌اند و حامی فعال جامعهٔ <strong>OSGeo</strong>، طراحی و
            توسعه داده شده است.
          </p>
          <a
            href="https://araz.me"
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1.5 mt-3 text-sm text-blue-600 hover:underline font-semibold"
          >
            🌐 araz.me
          </a>
        </section>

        {/* همکاری */}
        <section className="bg-gradient-to-l from-blue-50 to-indigo-50 rounded-3xl p-7 border border-blue-100">
          <h2 className="text-lg font-bold text-slate-800 mb-3 flex items-center gap-2">
            <span>🤝</span> به ما کمک کنید بهتر شویم
          </h2>
          <p className="text-slate-600 leading-relaxed text-sm">
            مپ‌آتون یک پروژهٔ در حال رشد است. هوش مصنوعی این سامانه با
            <strong> بازخورد شما</strong> آموزش می‌بیند و دقیق‌تر می‌شود. هر بار که
            نتیجه‌ای می‌بینید، با ثبت یک نظر کوتاه (درست بود؟ اشتباه بود؟ پیشنهادی
            دارید؟) مستقیماً به بهبود سامانه کمک می‌کنید.
          </p>
          <p className="text-slate-600 leading-relaxed text-sm mt-3">
            اگر برنامه‌نویس یا متخصص GIS هستید و علاقه‌مند به مشارکت در توسعهٔ این
            پروژه هستید، خوشحال می‌شویم با شما همکاری کنیم. 💙
          </p>
        </section>

        {/* حمایت */}
        <section className="text-center bg-white rounded-3xl p-7 border border-slate-100 shadow-sm">
          <h2 className="text-lg font-bold text-slate-800 mb-2 flex items-center justify-center gap-2">
            <span>☕</span> حمایت از پروژه
          </h2>
          <p className="text-slate-500 text-sm mb-4">
            اگر این پروژه برایتان مفید بود، می‌توانید با خرید یک قهوه از من حمایت کنید
          </p>
          <a href="https://www.coffeebede.com/arazshah" target="_blank" rel="noreferrer">
            <img
              className="mx-auto max-w-[260px] w-full hover:scale-105 transition"
              src="https://coffeebede.ir/DashboardTemplateV2/app-assets/images/banner/default-yellow.svg"
              alt="حمایت با قهوه"
            />
          </a>
        </section>

        {/* لینک‌ها */}
        <section className="flex justify-center gap-4 pt-2">
          <a href="https://github.com/arazshah" target="_blank" rel="noreferrer"
            className="text-sm text-slate-500 hover:text-slate-800 transition">GitHub</a>
          <span className="text-slate-300">·</span>
          <a href="https://linkedin.com/in/araz-shahkarami" target="_blank" rel="noreferrer"
            className="text-sm text-slate-500 hover:text-slate-800 transition">LinkedIn</a>
          <span className="text-slate-300">·</span>
          <a href="https://instagram.com/araz.me" target="_blank" rel="noreferrer"
            className="text-sm text-slate-500 hover:text-slate-800 transition">Instagram</a>
        </section>
      </main>

      <footer className="text-center py-6 text-xs text-slate-400">
        مپ‌آتون © 2026 · ساخته‌شده با 💙 توسط آراز شاه‌کرمی
      </footer>
    </div>
  );
}
