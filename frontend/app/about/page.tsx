"use client";
import {
  Sparkles, Target, Users, Code, ArrowLeft, Mail, Map,
  Brain, Database, Globe, Heart, Coffee, TrendingUp,
} from "lucide-react";
import Link from "next/link";

// آیکون‌های شبکه اجتماعی با SVG مستقیم
const GithubIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
    <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z"/>
  </svg>
);

const LinkedinIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
    <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
  </svg>
);

const InstagramIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
    <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 1 0 0 12.324 6.162 6.162 0 0 0 0-12.324zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm6.406-11.845a1.44 1.44 0 1 0 0 2.881 1.44 1.44 0 0 0 0-2.881z"/>
  </svg>
);

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-200 overflow-y-auto">
      <div className="max-w-4xl mx-auto px-6 py-12">

        {/* هدر */}
        <div className="flex items-center gap-4 mb-12">
          <Link href="/" className="text-slate-400 hover:text-white transition-colors">
            <ArrowLeft size={24} />
          </Link>
          <div className="flex items-center gap-2">
            <Sparkles className="text-blue-500" size={28} />
            <h1 className="text-3xl font-bold text-white">درباره مپ آتون</h1>
          </div>
        </div>

        {/* بنر معرفی */}
        <section className="mb-12">
          <div className="bg-gradient-to-br from-blue-900/40 to-purple-900/40 rounded-2xl p-8 border border-blue-800/30">
            <h2 className="text-2xl font-bold text-white mb-3">
              ماراتن نقشه‌های هوشمند 🗺️
            </h2>
            <p className="text-slate-300 leading-relaxed text-lg">
              «مپ آتون» ترکیبی از{" "}
              <span className="text-blue-400 font-semibold">Map</span> (نقشه) و{" "}
              <span className="text-purple-400 font-semibold">Marathon</span> (ماراتن) است؛
              تلاشی مستمر برای ساختن سامانه‌ای که زبان فارسی را می‌فهمد و دنیای جغرافیا را
              برای همه قابل دسترس می‌کند.
            </p>
          </div>
        </section>

        {/* سامانه چیست */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold text-blue-400 mb-4">سامانه چیست؟</h2>
          <p className="text-slate-300 leading-relaxed mb-4">
            مپ آتون (Mapathon) یک سامانه هوشمند جستجو و تحلیل مکانی است که با استفاده از
            هوش مصنوعی و داده‌های OpenStreetMap، به سوالات مکانی کاربران به زبان طبیعی فارسی
            پاسخ می‌دهد. کافیست سوال خود را مثل یک گفتگوی عادی بپرسید — مثلاً
            «نزدیک‌ترین مترو به میدان انقلاب کجاست؟» — و سامانه پاسخ را روی نقشه نشان می‌دهد.
          </p>
          <p className="text-slate-300 leading-relaxed">
            این سامانه قادر است فاصله بین مکان‌ها، مکان‌های نزدیک، مساحت مناطق و اطلاعات
            جغرافیایی مختلف را به صورت خودکار محاسبه و نمایش دهد. هر چه بیشتر با آن
            کار کنید و بازخورد بدهید، هوشمندتر و دقیق‌تر می‌شود.
          </p>
        </section>

        {/* ویژگی‌ها */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold text-blue-400 mb-4">ویژگی‌ها</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {[
              {
                icon: <Brain className="text-blue-500" size={24} />,
                title: "پردازش زبان طبیعی",
                desc: "سوال خود را به زبان فارسی روزمره بپرسید؛ نیازی به دانش فنی نیست.",
                border: "hover:border-blue-500/50",
              },
              {
                icon: <Target className="text-green-500" size={24} />,
                title: "تحلیل مکانی دقیق",
                desc: "محاسبه فاصله، مساحت، و یافتن مکان‌های نزدیک با موتور PostGIS.",
                border: "hover:border-green-500/50",
              },
              {
                icon: <Database className="text-purple-500" size={24} />,
                title: "داده‌های باز OSM",
                desc: "استفاده از داده‌های آزاد OpenStreetMap که توسط جامعه جهانی نگهداری می‌شود.",
                border: "hover:border-purple-500/50",
              },
              {
                icon: <TrendingUp className="text-yellow-500" size={24} />,
                title: "یادگیری مستمر",
                desc: "با بازخورد کاربران، سیستم به‌مرور بهتر و هوشمندتر می‌شود.",
                border: "hover:border-yellow-500/50",
              },
            ].map((item, i) => (
              <div
                key={i}
                className={`bg-slate-900 rounded-xl p-6 border border-slate-800 ${item.border} transition-colors`}
              >
                <div className="mb-3">{item.icon}</div>
                <h3 className="text-lg font-semibold text-white mb-2">{item.title}</h3>
                <p className="text-sm text-slate-400">{item.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* فناوری‌ها */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold text-blue-400 mb-4">فناوری‌های به‌کاررفته</h2>
          <div className="bg-slate-900 rounded-xl p-6 border border-slate-800">
            <div className="flex flex-wrap gap-3">
              {[
                "FastAPI", "PostgreSQL", "PostGIS", "Next.js",
                "TypeScript", "MapLibre GL", "OpenStreetMap",
                "LLM / GPT-4o", "Python", "SQLAlchemy",
                "Tailwind CSS", "Docker", "Coolify",
              ].map((tech) => (
                <span
                  key={tech}
                  className="px-3 py-1.5 bg-slate-800 text-slate-300 rounded-lg text-sm border border-slate-700"
                >
                  {tech}
                </span>
              ))}
            </div>
          </div>
        </section>

        {/* چرا این پروژه */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold text-blue-400 mb-4">چرا این پروژه؟</h2>
          <div className="bg-slate-900 rounded-xl p-6 border border-slate-800">
            <p className="text-slate-300 leading-relaxed mb-4">
              اطلاعات مکانی همه‌جا هستند، اما دسترسی به آن‌ها برای کاربر فارسی‌زبان همیشه
              آسان نبوده است. بیشتر ابزارهای GIS پیچیده‌اند و به دانش تخصصی نیاز دارند.
              هدف ما این است که این فاصله را پر کنیم:{" "}
              <span className="text-blue-400">
                هر کسی بتواند به زبان خودش از نقشه سوال بپرسد و پاسخ بگیرد.
              </span>
            </p>
            <p className="text-slate-300 leading-relaxed">
              این پروژه در راستای حمایت از جامعه{" "}
              <span className="text-green-400 font-semibold">OSGeo</span> و داده‌های باز توسعه
              می‌یابد. ما به این باور داریم که داده‌های جغرافیایی باید برای همه در دسترس باشند.
            </p>
          </div>
        </section>

        {/* فراخوان همکاری */}
        <section className="mb-12">
          <div className="bg-gradient-to-br from-green-900/30 to-blue-900/30 rounded-2xl p-8 border border-green-800/30">
            <div className="flex items-center gap-2 mb-3">
              <Users className="text-green-400" size={24} />
              <h2 className="text-2xl font-semibold text-white">به ما بپیوندید</h2>
            </div>
            <p className="text-slate-300 leading-relaxed">
              این پروژه در حال رشد است و به یاری متخصصان حوزه{" "}
              <span className="text-green-400 font-semibold">GIS</span>، توسعه‌دهندگان، و
              علاقه‌مندان به داده‌های مکانی نیاز دارد. اگر دوست دارید در توسعه و پیشرفت
              این سامانه سهیم باشید، خوشحال می‌شویم با ما در ارتباط باشید.
              هر بازخورد، پیشنهاد، یا مشارکتی ارزشمند است. 💚
            </p>
          </div>
        </section>

        {/* سازنده پروژه - آراز شاه کرمی */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold text-blue-400 mb-4">سازنده پروژه</h2>
          <div className="bg-slate-900 rounded-xl p-8 border border-slate-800">
            <div className="flex flex-col md:flex-row items-center md:items-start gap-6">
              <div className="w-24 h-24 bg-gradient-to-br from-blue-500 to-purple-500 rounded-2xl flex items-center justify-center flex-shrink-0">
                <Users className="text-white" size={40} />
              </div>
              <div className="flex-1 text-center md:text-right">
                <h3 className="text-2xl font-bold text-white mb-1">آراز شاه کرمی</h3>
                <p className="text-blue-400 font-medium mb-4">
                  مهندس هوش مصنوعی مکانی (Geospatial AI) — توسعه‌دهنده بک‌اند
                </p>
                <p className="text-slate-300 leading-relaxed mb-6">
                  آراز شاه کرمی مهندس هوش مصنوعی مکانی و توسعه‌دهنده بک‌اند با تجربه گسترده
                  در فناوری‌های نوین و حامی فعال جامعه{" "}
                  <span className="text-green-400">OSGeo</span> است. با تمرکز بر تلاقی هوش
                  مصنوعی و داده‌های جغرافیایی، به دنبال ساختن ابزارهایی است که قدرت تحلیل
                  مکانی را در اختیار همه قرار دهد — نه فقط متخصصان.
                </p>

                {/* لینک‌های شبکه اجتماعی */}
                <div className="flex flex-wrap justify-center md:justify-start gap-3">
                  <a
                    href="https://araz.me"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors text-sm font-medium"
                  >
                    <Globe size={16} />
                    araz.me
                  </a>
                  <a
                    href="https://github.com/arazshah"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg transition-colors text-sm border border-slate-700"
                  >
                    <GithubIcon />
                    GitHub
                  </a>
                  <a
                    href="https://linkedin.com/in/araz-shahkarami"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg transition-colors text-sm border border-slate-700"
                  >
                    <LinkedinIcon />
                    LinkedIn
                  </a>
                  <a
                    href="https://instagram.com/araz.me"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg transition-colors text-sm border border-slate-700"
                  >
                    <InstagramIcon />
                    Instagram
                  </a>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* حمایت - بنر قهوه */}
        <section className="mb-12">
          <div className="bg-gradient-to-br from-yellow-900/20 to-orange-900/20 rounded-2xl p-8 border border-yellow-800/30 text-center">
            <div className="flex items-center justify-center gap-2 mb-3">
              <Coffee className="text-yellow-400" size={24} />
              <h2 className="text-2xl font-semibold text-white">حمایت از پروژه</h2>
            </div>
            <p className="text-slate-300 leading-relaxed mb-6 max-w-2xl mx-auto">
              این پروژه با عشق و در اوقات فراغت توسعه می‌یابد. اگر مپ آتون برایتان مفید بوده
              و دوست دارید از ادامه‌ی این مسیر حمایت کنید، می‌توانید با خرید یک فنجان قهوه
              ما را دلگرم کنید. ☕ هر حمایتی، انگیزه‌ای برای بهتر شدن است.
            </p>
            <a
              href="https://www.coffeebede.com/arazshah"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block transition-transform hover:scale-105"
            >
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src="https://coffeebede.ir/DashboardTemplateV2/app-assets/images/banner/default-yellow.svg"
                alt="قهوه بده - حمایت از آراز شاه کرمی"
                className="mx-auto rounded-lg max-w-xs"
              />
            </a>
          </div>
        </section>

        {/* تماس */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold text-blue-400 mb-4">تماس با ما</h2>
          <div className="bg-slate-900 rounded-xl p-6 border border-slate-800 space-y-4">
            <div className="flex items-center gap-3">
              <Mail className="text-blue-500 flex-shrink-0" size={20} />
              <a href="mailto:info@mapathon.ir" className="text-slate-300 hover:text-blue-400 transition-colors">
                info@mapathon.ir
              </a>
            </div>
            <div className="flex items-center gap-3">
              <Map className="text-blue-500 flex-shrink-0" size={20} />
              <a href="https://mapathon.ir" target="_blank" rel="noopener noreferrer" className="text-slate-300 hover:text-blue-400 transition-colors">
                mapathon.ir
              </a>
            </div>
            <div className="flex items-center gap-3">
              <Globe className="text-blue-500 flex-shrink-0" size={20} />
              <a href="https://araz.me" target="_blank" rel="noopener noreferrer" className="text-slate-300 hover:text-blue-400 transition-colors">
                araz.me — وب‌سایت شخصی سازنده
              </a>
            </div>
          </div>
        </section>

        {/* فوتر */}
        <footer className="text-center text-slate-600 text-sm pt-8 border-t border-slate-800">
          <p className="flex items-center justify-center gap-1">
            ساخته‌شده با{" "}
            <Heart className="text-red-500 mx-1" size={14} fill="currentColor" />
            توسط{" "}
            <a
              href="https://araz.me"
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-400 hover:text-blue-300 mr-1"
            >
              آراز شاه کرمی
            </a>
          </p>
          <p className="mt-2">© ۱۴۰۵ مپ آتون — تمامی حقوق محفوظ است</p>
        </footer>

      </div>
    </div>
  );
}