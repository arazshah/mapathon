"use client";
import {
  Sparkles, Target, Users, Code, ArrowLeft, Mail, Map,
  Brain, Database, Globe, Github, Linkedin, Instagram,
  Heart, Coffee, MessageSquare, Zap, Layers, TrendingUp,
} from "lucide-react";
import Link from "next/link";

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
              «مپ آتون» ترکیبی از <span className="text-blue-400 font-semibold">Map</span> (نقشه) و{" "}
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
            پاسخ می‌دهد. کافیست سوال خود را مثل یک گفتگوی عادی بپرسید — مثلاً «نزدیک‌ترین مترو
            به میدان انقلاب کجاست؟» — و سامانه پاسخ را روی نقشه به شما نشان می‌دهد.
          </p>
          <p className="text-slate-300 leading-relaxed">
            این سامانه قادر است فاصله بین مکان‌ها، مکان‌های نزدیک، مساحت مناطق و اطلاعات
            جغرافیایی مختلف را به صورت خودکار محاسبه و نمایش دهد. هر چه بیشتر با آن کار کنید
            و بازخورد بدهید، هوشمندتر و دقیق‌تر می‌شود.
          </p>
        </section>

        {/* ویژگی‌ها */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold text-blue-400 mb-4">ویژگی‌ها</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-slate-900 rounded-xl p-6 border border-slate-800 hover:border-blue-500/50 transition-colors">
              <Brain className="text-blue-500 mb-3" size={24} />
              <h3 className="text-lg font-semibold text-white mb-2">پردازش زبان طبیعی</h3>
              <p className="text-sm text-slate-400">
                سوال خود را به زبان فارسی روزمره بپرسید؛ نیازی به دانش فنی نیست.
              </p>
            </div>
            <div className="bg-slate-900 rounded-xl p-6 border border-slate-800 hover:border-green-500/50 transition-colors">
              <Target className="text-green-500 mb-3" size={24} />
              <h3 className="text-lg font-semibold text-white mb-2">تحلیل مکانی دقیق</h3>
              <p className="text-sm text-slate-400">
                محاسبه فاصله، مساحت، و یافتن مکان‌های نزدیک با موتور PostGIS.
              </p>
            </div>
            <div className="bg-slate-900 rounded-xl p-6 border border-slate-800 hover:border-purple-500/50 transition-colors">
              <Database className="text-purple-500 mb-3" size={24} />
              <h3 className="text-lg font-semibold text-white mb-2">داده‌های باز OSM</h3>
              <p className="text-sm text-slate-400">
                استفاده از داده‌های آزاد OpenStreetMap که توسط جامعه جهانی نگهداری می‌شود.
              </p>
            </div>
            <div className="bg-slate-900 rounded-xl p-6 border border-slate-800 hover:border-yellow-500/50 transition-colors">
              <TrendingUp className="text-yellow-500 mb-3" size={24} />
              <h3 className="text-lg font-semibold text-white mb-2">یادگیری مستمر</h3>
              <p className="text-sm text-slate-400">
                با بازخورد کاربران، سیستم به‌مرور بهتر و هوشمندتر می‌شود.
              </p>
            </div>
          </div>
        </section>

        {/* فناوری‌ها */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold text-blue-400 mb-4">فناوری‌های به‌کاررفته</h2>
          <div className="bg-slate-900 rounded-xl p-6 border border-slate-800">
            <div className="flex flex-wrap gap-3">
              {[
                "FastAPI", "PostgreSQL", "PostGIS", "Next.js",
                "TypeScript", "MapLibre GL", "OpenStreetMap", "LLM (GPT)",
                "Python", "SQLAlchemy", "Tailwind CSS",
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

        {/* هدف */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold text-blue-400 mb-4">چرا این پروژه؟</h2>
          <div className="bg-slate-900 rounded-xl p-6 border border-slate-800">
            <p className="text-slate-300 leading-relaxed mb-4">
              اطلاعات مکانی همه‌جا هستند، اما دسترسی به آن‌ها برای کاربر فارسی‌زبان همیشه آسان
              نبوده است. بیشتر ابزارهای GIS پیچیده‌اند و به دانش تخصصی نیاز دارند.
              هدف ما این است که این فاصله را پر کنیم: <span className="text-blue-400">
              هر کسی بتواند به زبان خودش از نقشه سوال بپرسد و پاسخ بگیرد.</span>
            </p>
            <p className="text-slate-300 leading-relaxed">
              این پروژه به‌صورت متن‌باز و در راستای حمایت از جامعه{" "}
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
              علاقه‌مندان به داده‌های مکانی نیاز دارد. اگر دوست دارید در توسعه و پیشرفت این
              سامانه سهیم باشید، خوشحال می‌شویم با ما در ارتباط باشید. هر بازخورد، پیشنهاد،
              یا مشارکتی ارزشمند است. 💚
            </p>
          </div>
        </section>

        {/* تیم توسعه - آراز شاه کرمی */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold text-blue-400 mb-4">سازنده پروژه</h2>
          <div className="bg-slate-900 rounded-xl p-8 border border-slate-800">
            <div className="flex flex-col md:flex-row items-center md:items-start gap-6">
              <div className="w-24 h-24 bg-gradient-to-br from-blue-500 to-purple-500 rounded-2xl flex items-center justify-center flex-shrink-0">
                <Users className="text-white" size={40} />
              </div>
              <div className="flex-1 text-center md:text-right">
                <h3 className="text-2xl font-bold text-white mb-1">آراز شاه کرمی</h3>
                <p className="text-blue-400 font-medium mb-3">
                  مهندس هوش مصنوعی مکانی و توسعه‌دهنده بک‌اند
                </p>
                <p className="text-slate-300 leading-relaxed mb-5">
                  مهندس هوش مصنوعی مکانی (Geospatial AI) و توسعه‌دهنده بک‌اند با تجربه‌ای
                  گسترده در زمینه فناوری‌های نوین، و حامی فعال جامعه{" "}
                  <span className="text-green-400">OSGeo</span>. آراز با تمرکز بر تلاقی هوش
                  مصنوعی و داده‌های جغرافیایی، به دنبال ساختن ابزارهایی است که قدرت تحلیل مکانی
                  را در اختیار همه قرار دهد.
                </p>

                {/* لینک‌ها */}
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
                    <Github size={16} />
                    GitHub
                  </a>
                  <a
                    href="https://linkedin.com/in/araz-shahkarami"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg transition-colors text-sm border border-slate-700"
                  >
                    <Linkedin size={16} />
                    LinkedIn
                  </a>
                  <a
                    href="https://instagram.com/araz.me"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg transition-colors text-sm border border-slate-700"
                  >
                    <Instagram size={16} />
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
                className="img-fluid mx-auto rounded-lg"
                src="https://coffeebede.ir/DashboardTemplateV2/app-assets/images/banner/default-yellow.svg"
                alt="قهوه بده - حمایت از آراز شاه کرمی"
              />
            </a>
          </div>
        </section>

        {/* تماس */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold text-blue-400 mb-4">تماس با ما</h2>
          <div className="bg-slate-900 rounded-xl p-6 border border-slate-800 space-y-3">
            <div className="flex items-center gap-3">
              <Mail className="text-blue-500" size={20} />
              <a href="mailto:info@mapathon.ir" className="text-slate-300 hover:text-blue-400 transition-colors">
                info@mapathon.ir
              </a>
            </div>
            <div className="flex items-center gap-3">
              <Map className="text-blue-500" size={20} />
              <a href="https://mapathon.ir" className="text-slate-300 hover:text-blue-400 transition-colors">
                mapathon.ir
              </a>
            </div>
            <div className="flex items-center gap-3">
              <Globe className="text-blue-500" size={20} />
              <a href="https://araz.me" target="_blank" rel="noopener noreferrer" className="text-slate-300 hover:text-blue-400 transition-colors">
                araz.me — وب‌سایت شخصی سازنده
              </a>
            </div>
          </div>
        </section>

        {/* فوتر */}
        <footer className="text-center text-slate-600 text-sm pt-8 border-t border-slate-800">
          <p className="flex items-center justify-center gap-1">
            ساخته‌شده با <Heart className="text-red-500" size={14} fill="currentColor" /> توسط{" "}
            <a href="https://araz.me" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300">
              آراز شاه کرمی
            </a>
          </p>
          <p className="mt-2">© ۱۴۰۵ مپ آتون — تمامی حقوق محفوظ است</p>
        </footer>
      </div>
    </div>
  );
}