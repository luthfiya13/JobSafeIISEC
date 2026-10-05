"use client";

import React from "react";
import Link from "next/link";
import {
  ShieldCheck,
  ShieldAlert,
  ArrowRight,
  FileText,
  Cpu,
  Gauge,
  CheckSquare,
  ChevronRight
} from "lucide-react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import RiskGauge from "@/components/RiskGauge";
import { STATIC_INDICATORS } from "@/lib/mockData";

export default function LandingPage() {
  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900 selection:bg-blue-100 selection:text-blue-900">
      <Navbar />

      <main className="flex-1">
        {/* HERO SECTION */}
        <section className="relative pt-12 pb-20 sm:pt-20 sm:pb-28 overflow-hidden">
          {/* Subtle background pattern */}
          <div className="absolute inset-0 bg-[radial-gradient(#e2e8f0_1px,transparent_1px)] [background-size:24px_24px] opacity-40 pointer-events-none" />

          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative">
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-8 items-center">
              {/* Left Column: Headlines & CTA */}
              <div className="lg:col-span-7 space-y-6 text-center lg:text-left">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 border border-blue-200/80 text-blue-700 text-xs font-semibold tracking-wide">
                  <ShieldCheck className="w-3.5 h-3.5" />
                  <span>Platform Penilaian Risiko Lowongan Kerja Digital</span>
                </div>

                <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-slate-900 leading-[1.12]">
                  Cek Risiko Lowongan Kerja Sebelum Terlambat.
                </h1>

                <p className="text-base sm:text-lg text-slate-600 leading-relaxed max-w-2xl mx-auto lg:mx-0">
                  JOBSAFE membantu mengidentifikasi tanda-tanda risiko pada lowongan kerja digital dan memberikan panduan verifikasi sebelum Anda melamar.
                </p>

                {/* Primary & Secondary Buttons */}
                <div className="flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-3.5 pt-2">
                  <Link
                    href="/periksa"
                    className="w-full sm:w-auto inline-flex items-center justify-center gap-2.5 px-7 py-3.5 rounded-xl bg-slate-900 text-white font-semibold text-sm hover:bg-blue-600 transition-all shadow-sm hover:shadow active:scale-98"
                  >
                    <span>Cek Lowongan Sekarang</span>
                    <ArrowRight className="w-4 h-4 text-blue-300" />
                  </Link>

                  <a
                    href="#cara-kerja"
                    className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl bg-white border border-slate-200 text-slate-700 font-semibold text-sm hover:bg-slate-50 hover:border-slate-300 transition-colors"
                  >
                    Pelajari Cara Kerja
                  </a>
                </div>

                {/* Trust message */}
                <div className="pt-4 flex items-center justify-center lg:justify-start gap-2 text-xs font-medium text-slate-500">
                  <span className="inline-block w-2 h-2 rounded-full bg-emerald-500" />
                  <span>Gratis</span>
                  <span className="text-slate-300">•</span>
                  <span>Tanpa Login</span>
                  <span className="text-slate-300">•</span>
                  <span>Analisis Berbasis Indikator</span>
                </div>
              </div>

              {/* Right Column: Sleek Risk Meter Mockup Preview */}
              <div className="lg:col-span-5 flex justify-center">
                <div className="w-full max-w-md bg-white rounded-3xl border border-slate-200 p-6 sm:p-7 shadow-sm relative">
                  {/* Mock card header */}
                  <div className="flex items-center justify-between pb-4 border-b border-slate-100 mb-5">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full bg-red-400" />
                      <div className="w-3 h-3 rounded-full bg-amber-400" />
                      <div className="w-3 h-3 rounded-full bg-emerald-400" />
                    </div>
                    <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                      Simulasi Penilaian
                    </span>
                  </div>

                  {/* Render Gauge */}
                  <RiskGauge
                    score={72}
                    level="RISIKO TINGGI"
                    color="red"
                    size={240}
                  />

                  {/* Mock snippet summary */}
                  <div className="mt-5 p-3.5 rounded-xl bg-slate-50 border border-slate-200/80 text-xs space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-slate-700">Ringkasan Terdeteksi:</span>
                      <span className="text-red-600 font-bold">5 Indikator</span>
                    </div>
                    <p className="text-slate-500 leading-relaxed text-[11px]">
                      Terdeteksi permintaan deposit di awal (R1), imbalan harian tidak wajar (R2), dan tugas like berbayar (R6).
                    </p>
                  </div>

                  <div className="mt-4 text-center">
                    <Link
                      href="/periksa"
                      className="text-xs font-semibold text-blue-600 hover:text-blue-700 inline-flex items-center gap-1"
                    >
                      Coba periksa lowongan Anda sekarang <ChevronRight className="w-3.5 h-3.5" />
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* SECTION CARA KERJA (4 LANGKAH) */}
        <section id="cara-kerja" className="py-20 bg-white border-y border-slate-200/70">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center max-w-2xl mx-auto mb-16">
              <span className="text-xs font-bold uppercase tracking-wider text-blue-600 bg-blue-50 px-3 py-1 rounded-full border border-blue-100">
                Alur Sederhana
              </span>
              <h2 className="text-3xl font-extrabold text-slate-900 tracking-tight mt-3">
                Cara Kerja JOBSAFE
              </h2>
              <p className="text-slate-600 text-sm mt-2">
                Empat langkah cepat untuk memverifikasi keabsahan lowongan kerja sebelum Anda melamar atau menyerahkan data pribadi.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {/* Step 1 */}
              <div className="clean-card p-6 relative flex flex-col justify-between">
                <div>
                  <span className="text-xs font-extrabold text-blue-600 bg-blue-50 px-2.5 py-1 rounded-md mb-4 inline-block">
                    LANGKAH 01
                  </span>
                  <div className="w-12 h-12 rounded-xl bg-slate-900 text-white flex items-center justify-center mb-4">
                    <FileText className="w-6 h-6 text-blue-400" />
                  </div>
                  <h3 className="text-lg font-bold text-slate-900 mb-2">
                    Masukkan Lowongan
                  </h3>
                  <p className="text-xs text-slate-600 leading-relaxed">
                    Tempel teks lowongan, unggah foto screenshot, atau masukkan tautan postingan lowongan kerja yang ingin Anda periksa.
                  </p>
                </div>
              </div>

              {/* Step 2 */}
              <div className="clean-card p-6 relative flex flex-col justify-between">
                <div>
                  <span className="text-xs font-extrabold text-blue-600 bg-blue-50 px-2.5 py-1 rounded-md mb-4 inline-block">
                    LANGKAH 02
                  </span>
                  <div className="w-12 h-12 rounded-xl bg-slate-900 text-white flex items-center justify-center mb-4">
                    <Cpu className="w-6 h-6 text-blue-400" />
                  </div>
                  <h3 className="text-lg font-bold text-slate-900 mb-2">
                    Sistem Menganalisis
                  </h3>
                  <p className="text-xs text-slate-600 leading-relaxed">
                    Sistem mengekstraksi informasi dan memeriksa kesesuaian pola teks terhadap 10 indikator risiko digital secara objektif.
                  </p>
                </div>
              </div>

              {/* Step 3 */}
              <div className="clean-card p-6 relative flex flex-col justify-between">
                <div>
                  <span className="text-xs font-extrabold text-blue-600 bg-blue-50 px-2.5 py-1 rounded-md mb-4 inline-block">
                    LANGKAH 03
                  </span>
                  <div className="w-12 h-12 rounded-xl bg-slate-900 text-white flex items-center justify-center mb-4">
                    <Gauge className="w-6 h-6 text-blue-400" />
                  </div>
                  <h3 className="text-lg font-bold text-slate-900 mb-2">
                    Lihat Risk Score
                  </h3>
                  <p className="text-xs text-slate-600 leading-relaxed">
                    Sistem menghasilkan tingkat risiko (Rendah, Sedang, atau Tinggi), skor 0–100, serta cuplikan bukti indikator yang ditemukan.
                  </p>
                </div>
              </div>

              {/* Step 4 */}
              <div className="clean-card p-6 relative flex flex-col justify-between">
                <div>
                  <span className="text-xs font-extrabold text-blue-600 bg-blue-50 px-2.5 py-1 rounded-md mb-4 inline-block">
                    LANGKAH 04
                  </span>
                  <div className="w-12 h-12 rounded-xl bg-slate-900 text-white flex items-center justify-center mb-4">
                    <CheckSquare className="w-6 h-6 text-blue-400" />
                  </div>
                  <h3 className="text-lg font-bold text-slate-900 mb-2">
                    Lakukan Verifikasi
                  </h3>
                  <p className="text-xs text-slate-600 leading-relaxed">
                    Gunakan panduan checklist verifikasi interaktif untuk memeriksa kredibilitas perusahaan secara mandiri dan aman.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* SECTION 10 INDIKATOR RISIKO */}
        <section id="indikator" className="py-20 bg-slate-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center max-w-2xl mx-auto mb-16">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-600 bg-white px-3 py-1 rounded-full border border-slate-200 shadow-xs">
                Kamus Risiko
              </span>
              <h2 className="text-3xl font-extrabold text-slate-900 tracking-tight mt-3">
                10 Indikator Risiko Digital
              </h2>
              <p className="text-slate-600 text-sm mt-2">
                JOBSAFE menggunakan model pembobotan terstruktur untuk mendeteksi anomali pada penawaran kerja digital (Total Bobot 100%).
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {STATIC_INDICATORS.map((ind) => (
                <div
                  key={ind.code}
                  className="clean-card p-5 bg-white hover:border-slate-300 transition-colors flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-center justify-between gap-2 mb-2">
                      <span className="text-xs font-extrabold text-blue-600 bg-blue-50 px-2 py-0.5 rounded-md border border-blue-100">
                        {ind.code}
                      </span>
                      <span className="text-xs font-bold text-slate-500 bg-slate-100 px-2 py-0.5 rounded-md">
                        Bobot {ind.weight}%
                      </span>
                    </div>

                    <h3 className="text-base font-bold text-slate-900 mb-1.5">
                      {ind.name}
                    </h3>
                    <p className="text-xs text-slate-600 leading-relaxed mb-3">
                      {ind.description}
                    </p>
                  </div>

                  <div className="pt-3 border-t border-slate-100">
                    <span className="text-[11px] font-semibold text-slate-400 block mb-0.5">
                      Mengapa diwaspadai:
                    </span>
                    <p className="text-[11px] text-slate-500 leading-snug">
                      {ind.why_important}
                    </p>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-12 text-center">
              <Link
                href="/periksa"
                className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-slate-900 text-white font-semibold text-sm hover:bg-blue-600 transition-colors"
              >
                <span>Uji Coba Lowongan Anda dengan 10 Indikator Ini</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>
        </section>

        {/* SECTION TENTANG JOBSAFE */}
        <section id="tentang" className="py-20 bg-white border-t border-slate-200/80">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center space-y-6">
            <div className="w-12 h-12 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center mx-auto">
              <ShieldAlert className="w-6 h-6" />
            </div>

            <h2 className="text-3xl font-extrabold text-slate-900 tracking-tight">
              Filosofi Penilaian Risiko JOBSAFE
            </h2>

            <p className="text-slate-600 text-sm sm:text-base leading-relaxed">
              Tujuan utama JOBSAFE adalah memberikan <strong>risk assessment</strong> terhadap lowongan kerja, bukan memberikan keputusan mutlak bahwa sebuah lowongan pasti palsu atau pasti aman. Sistem menyajikan <strong>tingkat risiko, indikator yang terdeteksi, alasan risiko, dan langkah verifikasi mandiri</strong> agar pencari kerja dapat mengambil keputusan secara mandiri dan rasional.
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-6 text-left">
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
                <h4 className="font-bold text-slate-900 text-sm mb-1">Objektif &amp; Terbuka</h4>
                <p className="text-xs text-slate-500 leading-relaxed">
                  Setiap skor memiliki rincian bukti teks dan alasan mengapa indikator tersebut perlu diwaspadai.
                </p>
              </div>

              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
                <h4 className="font-bold text-slate-900 text-sm mb-1">Privasi Terjaga Penuh</h4>
                <p className="text-xs text-slate-500 leading-relaxed">
                  Pengguna tidak perlu mendaftar atau memberikan email/nomor kontak untuk menggunakan sistem.
                </p>
              </div>

              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
                <h4 className="font-bold text-slate-900 text-sm mb-1">Panduan Aplikatif</h4>
                <p className="text-xs text-slate-500 leading-relaxed">
                  Dilengkapi checklist verifikasi sebelum Anda memutuskan untuk melanjutkan proses lamaran.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* BOTTOM CTA BANNER */}
        <section className="py-16 bg-slate-900 text-white">
          <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 text-center space-y-5">
            <h2 className="text-2xl sm:text-3xl font-bold tracking-tight">
              Punya lowongan kerja digital yang meragukan?
            </h2>
            <p className="text-slate-300 text-sm max-w-xl mx-auto leading-relaxed">
              Jangan terburu-buru mentransfer uang atau membagikan data identitas sensitif. Periksa risikonya dalam hitungan detik.
            </p>
            <div className="pt-2">
              <Link
                href="/periksa"
                className="inline-flex items-center gap-2 px-8 py-3.5 rounded-xl bg-blue-600 text-white font-semibold text-sm hover:bg-blue-500 transition-all shadow-md active:scale-98"
              >
                <span>Periksa Lowongan Sekarang</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}
