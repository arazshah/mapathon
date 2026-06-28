import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "مپ آتون | ماراتن نقشه‌های هوشمند",
  description: "سامانه هوشمند جستجو و تحلیل مکانی",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="fa" dir="rtl">
      <head>
        <link 
          rel="stylesheet" 
          href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" 
        />
      </head>
      <body className="antialiased">{children}</body>
    </html>
  );
}
