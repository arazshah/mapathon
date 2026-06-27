import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "مپ‌آتون | ماراتن نقشه‌های هوشمند",
  description: "سامانه هوشمند پرس‌وجوی جغرافیایی برای ایران — سوال مکانی به زبان طبیعی بپرسید",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fa" dir="rtl">
      <body suppressHydrationWarning>{children}</body>
    </html>
  );
}
