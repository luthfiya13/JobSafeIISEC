import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "JOBSAFE — Penilaian Risiko Lowongan Kerja Digital",
  description:
    "JOBSAFE membantu mengidentifikasi tanda-tanda risiko pada lowongan kerja digital dan memberikan panduan verifikasi sebelum Anda melamar.",
  icons: {
    icon: "/favicon.ico",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="id" className="h-full antialiased scroll-smooth">
      <body className="min-h-full flex flex-col font-sans bg-slate-50 text-slate-900">
        {children}
      </body>
    </html>
  );
}
