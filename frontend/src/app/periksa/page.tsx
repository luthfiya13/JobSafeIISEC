"use client";

import React, { useState, useRef } from "react";
import Image from "next/image";
import Link from "next/link";
import {
  FileText,
  Image as ImageIcon,
  Link as LinkIcon,
  UploadCloud,
  X,
  AlertCircle,
  RotateCcw,
  Printer,
  Sparkles,
  Info
} from "lucide-react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import RiskGauge from "@/components/RiskGauge";
import IndicatorCard from "@/components/IndicatorCard";
import IndicatorModal from "@/components/IndicatorModal";
import VerificationChecklist from "@/components/VerificationChecklist";
import LoadingAnalysis from "@/components/LoadingAnalysis";
import {
  AnalysisResult,
  IndicatorItem,
  analyzeText,
  analyzeUrl,
  analyzePhoto
} from "@/lib/api";
import { PRESET_JOBS } from "@/lib/mockData";

export default function PeriksaPage() {
  // Input states
  const [activeTab, setActiveTab] = useState<"text" | "photo" | "link">("text");
  const [textContent, setTextContent] = useState("");
  const [urlContent, setUrlContent] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [filePreview, setFilePreview] = useState<string | null>(null);

  // Flow states
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [selectedIndicator, setSelectedIndicator] = useState<IndicatorItem | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  // File selection handler
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setErrorMsg(null);
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (!["image/png", "image/jpeg", "image/jpg"].includes(file.type)) {
        setErrorMsg("Harap pilih berkas gambar berformat PNG, JPG, atau JPEG.");
        return;
      }
      setSelectedFile(file);
      const reader = new FileReader();
      reader.onload = (event) => {
        setFilePreview(event.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    setFilePreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  // Preset job loader
  const handleLoadPreset = (preset: typeof PRESET_JOBS[0]) => {
    setActiveTab("text");
    setTextContent(preset.text);
    setErrorMsg(null);
  };

  // Run Analysis Handler
  const handleRunAnalysis = async () => {
    setErrorMsg(null);

    if (activeTab === "text") {
      const trimmed = textContent.trim();
      if (!trimmed) {
        setErrorMsg("Teks lowongan belum diisi. Tempel teks lowongan kerja yang ingin diperiksa.");
        return;
      }
      if (trimmed.length < 20) {
        setErrorMsg("Teks lowongan terlalu pendek. Masukkan minimal 20 karakter agar analisis dapat bekerja akurat.");
        return;
      }

      setIsLoading(true);
      try {
        const res = await analyzeText(trimmed);
        setResult(res);
      } catch (err: unknown) {
        const message = err instanceof Error ? err.message : "Gagal menganalisis teks lowongan.";
        setErrorMsg(message);
      } finally {
        setIsLoading(false);
      }
    } else if (activeTab === "link") {
      const trimmedUrl = urlContent.trim();
      if (!trimmedUrl) {
        setErrorMsg("Tautan lowongan belum diisi. Masukkan URL postingan yang ingin diperiksa.");
        return;
      }
      if (!trimmedUrl.startsWith("http://") && !trimmedUrl.startsWith("https://")) {
        setErrorMsg("Tautan harus diawali dengan http:// atau https://");
        return;
      }

      setIsLoading(true);
      try {
        const res = await analyzeUrl(trimmedUrl);
        setResult(res);
      } catch (err: unknown) {
        const message = err instanceof Error
          ? err.message
          : "Kami belum dapat membaca lowongan dari tautan ini. Silakan salin teks lowongan dan tempelkan ke tab Teks.";
        setErrorMsg(message);
      } finally {
        setIsLoading(false);
      }
    } else if (activeTab === "photo") {
      if (!selectedFile) {
        setErrorMsg("Foto lowongan belum dipilih. Unggah screenshot postingan lowongan kerja.");
        return;
      }

      setIsLoading(true);
      try {
        const res = await analyzePhoto(selectedFile);
        setResult(res);
      } catch (err: unknown) {
        const message = err instanceof Error
          ? err.message
          : "Kami belum dapat membaca teks foto ini dengan jelas. Silakan pilih gambar yang lebih jelas atau gunakan tab Teks.";
        setErrorMsg(message);
      } finally {
        setIsLoading(false);
      }
    }
  };

  // Reset analysis to check another
  const handleReset = () => {
    setResult(null);
    setErrorMsg(null);
    setTextContent("");
    setUrlContent("");
    setSelectedFile(null);
    setFilePreview(null);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  // Print/Export
  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900 selection:bg-blue-100">
      <Navbar />

      <main className="flex-1 max-w-5xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12">
        {/* If loading is active, show the 5-step progress screen */}
        {isLoading && (
          <LoadingAnalysis
            inputType={activeTab}
          />
        )}

        {/* INPUT SECTION (Shown when not loading and no result yet) */}
        {!isLoading && !result && (
          <div className="space-y-8 animate-in fade-in duration-300">
            {/* Header */}
            <div className="text-center max-w-2xl mx-auto space-y-2">
              <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-slate-900">
                Periksa Lowongan Kerja
              </h1>
              <p className="text-slate-600 text-sm sm:text-base">
                Masukkan informasi lowongan yang ingin Anda periksa. Pilih metode input teks, foto screenshot, atau tautan.
              </p>
            </div>

            {/* Presets Quick Selectors */}
            <div className="bg-white rounded-2xl border border-slate-200 p-4 shadow-xs">
              <div className="flex items-center gap-2 mb-2.5">
                <Sparkles className="w-4 h-4 text-blue-600" />
                <span className="text-xs font-bold uppercase tracking-wider text-slate-700">
                  Uji Coba Cepat dengan Contoh Nyata:
                </span>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2">
                {PRESET_JOBS.map((preset) => (
                  <button
                    key={preset.id}
                    type="button"
                    onClick={() => handleLoadPreset(preset)}
                    className="text-left p-2.5 rounded-lg border border-slate-200/80 bg-slate-50 hover:bg-blue-50/60 hover:border-blue-300 transition-all text-xs flex flex-col justify-between"
                  >
                    <span className="font-semibold text-slate-900 line-clamp-1">
                      {preset.title.split("(")[0]}
                    </span>
                    <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded-md border mt-1.5 w-fit ${preset.badgeColor}`}>
                      {preset.badge}
                    </span>
                  </button>
                ))}
              </div>
            </div>

            {/* Main Input Card with 3 Tabs */}
            <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
              {/* Tab Navigation */}
              <div className="flex border-b border-slate-200 bg-slate-50/60">
                <button
                  type="button"
                  onClick={() => {
                    setActiveTab("text");
                    setErrorMsg(null);
                  }}
                  className={`flex-1 py-3.5 px-4 text-center text-sm font-semibold flex items-center justify-center gap-2 border-b-2 transition-all ${
                    activeTab === "text"
                      ? "border-blue-600 text-blue-600 bg-white"
                      : "border-transparent text-slate-500 hover:text-slate-800"
                  }`}
                >
                  <FileText className="w-4 h-4" />
                  <span>Tab 1 — Teks</span>
                </button>

                <button
                  type="button"
                  onClick={() => {
                    setActiveTab("photo");
                    setErrorMsg(null);
                  }}
                  className={`flex-1 py-3.5 px-4 text-center text-sm font-semibold flex items-center justify-center gap-2 border-b-2 transition-all ${
                    activeTab === "photo"
                      ? "border-blue-600 text-blue-600 bg-white"
                      : "border-transparent text-slate-500 hover:text-slate-800"
                  }`}
                >
                  <ImageIcon className="w-4 h-4" />
                  <span>Tab 2 — Foto</span>
                </button>

                <button
                  type="button"
                  onClick={() => {
                    setActiveTab("link");
                    setErrorMsg(null);
                  }}
                  className={`flex-1 py-3.5 px-4 text-center text-sm font-semibold flex items-center justify-center gap-2 border-b-2 transition-all ${
                    activeTab === "link"
                      ? "border-blue-600 text-blue-600 bg-white"
                      : "border-transparent text-slate-500 hover:text-slate-800"
                  }`}
                >
                  <LinkIcon className="w-4 h-4" />
                  <span>Tab 3 — Link</span>
                </button>
              </div>

              {/* Tab Contents */}
              <div className="p-6 sm:p-8">
                {/* TAB 1: TEXT */}
                {activeTab === "text" && (
                  <div className="space-y-4">
                    <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider">
                      Tempel teks lowongan kerja di sini:
                    </label>
                    <textarea
                      rows={9}
                      value={textContent}
                      onChange={(e) => setTextContent(e.target.value)}
                      placeholder="Dicari Admin Online, kerja dari rumah, penghasilan Rp500.000–Rp1.000.000/hari..."
                      className="w-full p-4 rounded-xl border border-slate-200 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-hidden focus:ring-2 focus:ring-blue-600 focus:border-transparent transition-all leading-relaxed"
                    />
                    <div className="flex items-center justify-between text-xs text-slate-400">
                      <span>{textContent.length} karakter</span>
                      <span>Minimal 20 karakter</span>
                    </div>

                    <button
                      type="button"
                      onClick={handleRunAnalysis}
                      className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-slate-900 text-white font-semibold text-sm hover:bg-blue-600 transition-all shadow-xs active:scale-98"
                    >
                      Analisis Lowongan
                    </button>
                  </div>
                )}

                {/* TAB 2: PHOTO */}
                {activeTab === "photo" && (
                  <div className="space-y-5">
                    <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider">
                      Upload screenshot lowongan:
                    </label>

                    {!filePreview ? (
                      <div
                        onClick={() => fileInputRef.current?.click()}
                        className="border-2 border-dashed border-slate-300 rounded-2xl p-8 sm:p-12 text-center cursor-pointer hover:border-blue-400 hover:bg-blue-50/20 transition-all"
                      >
                        <input
                          ref={fileInputRef}
                          type="file"
                          accept="image/png, image/jpeg, image/jpg"
                          onChange={handleFileChange}
                          className="hidden"
                        />
                        <div className="w-14 h-14 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center mx-auto mb-3">
                          <UploadCloud className="w-7 h-7" />
                        </div>
                        <h4 className="font-bold text-slate-800 text-sm mb-1">
                          Upload screenshot lowongan
                        </h4>
                        <p className="text-xs text-slate-500 mb-4">
                          PNG, JPG atau JPEG (Maks. 10MB)
                        </p>
                        <button
                          type="button"
                          className="px-5 py-2.5 rounded-lg bg-slate-100 text-slate-700 text-xs font-semibold hover:bg-slate-200 transition-colors pointer-events-none"
                        >
                          Pilih Foto
                        </button>
                      </div>
                    ) : (
                      <div className="space-y-4">
                        <div className="relative rounded-2xl border border-slate-200 overflow-hidden bg-slate-900/5 max-h-96 flex items-center justify-center p-2">
                          <Image
                            src={filePreview}
                            alt="Screenshot preview"
                            width={1200}
                            height={800}
                            unoptimized
                            className="max-h-80 w-auto object-contain rounded-lg"
                          />
                          <button
                            type="button"
                            onClick={handleRemoveFile}
                            className="absolute top-4 right-4 p-2 rounded-full bg-slate-900/80 text-white hover:bg-red-600 transition-colors shadow-md"
                            aria-label="Hapus foto"
                          >
                            <X className="w-4 h-4" />
                          </button>
                        </div>

                        <div className="flex items-center gap-3">
                          <button
                            type="button"
                            onClick={handleRunAnalysis}
                            className="px-8 py-3.5 rounded-xl bg-slate-900 text-white font-semibold text-sm hover:bg-blue-600 transition-all shadow-xs active:scale-98"
                          >
                            Analisis Foto
                          </button>
                          <button
                            type="button"
                            onClick={handleRemoveFile}
                            className="px-5 py-3.5 rounded-xl border border-slate-200 text-slate-600 text-sm font-semibold hover:bg-slate-50 transition-colors"
                          >
                            Ganti Foto
                          </button>
                        </div>
                      </div>
                    )}

                    <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 text-xs text-slate-500 flex items-start gap-2">
                      <Info className="w-4 h-4 text-blue-500 shrink-0 mt-0.5" />
                      <span>
                        Sistem akan membaca teks dari foto secara otomatis. Setelah analisis selesai, Anda dapat mengecek teks yang berhasil diekstrak di laporan hasil.
                      </span>
                    </div>
                  </div>
                )}

                {/* TAB 3: LINK */}
                {activeTab === "link" && (
                  <div className="space-y-5">
                    <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider">
                      Masukkan tautan / URL lowongan kerja:
                    </label>

                    <div className="relative">
                      <input
                        type="url"
                        value={urlContent}
                        onChange={(e) => setUrlContent(e.target.value)}
                        placeholder="https://..."
                        className="w-full pl-11 pr-4 py-3.5 rounded-xl border border-slate-200 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-hidden focus:ring-2 focus:ring-blue-600 focus:border-transparent transition-all"
                      />
                      <LinkIcon className="w-4 h-4 text-slate-400 absolute left-4 top-1/2 -translate-y-1/2" />
                    </div>

                    <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 text-xs text-slate-500 flex items-start gap-2">
                      <Info className="w-4 h-4 text-blue-500 shrink-0 mt-0.5" />
                      <span>
                        Alur pemrosesan: Link → Ekstraksi Konten Web → Text Extraction → Analisis Risiko.
                      </span>
                    </div>

                    <button
                      type="button"
                      onClick={handleRunAnalysis}
                      className="px-8 py-3.5 rounded-xl bg-slate-900 text-white font-semibold text-sm hover:bg-blue-600 transition-all shadow-xs active:scale-98"
                    >
                      Analisis Link
                    </button>
                  </div>
                )}

                {/* Error Banner */}
                {errorMsg && (
                  <div className="mt-5 p-4 rounded-xl bg-red-50 border border-red-200 text-red-800 text-sm flex items-start gap-3 animate-in fade-in duration-200">
                    <AlertCircle className="w-5 h-5 text-red-600 shrink-0 mt-0.5" />
                    <div className="flex-1">
                      <p className="font-semibold text-red-900">Kami belum dapat membaca lowongan ini.</p>
                      <p className="text-xs text-red-700 mt-0.5">{errorMsg}</p>
                      {activeTab !== "text" && (
                        <button
                          type="button"
                          onClick={() => {
                            setActiveTab("text");
                            setErrorMsg(null);
                          }}
                          className="mt-2 text-xs font-bold text-red-900 underline hover:text-red-950"
                        >
                          → Beralih ke Tab Teks untuk memasukkan teks secara manual
                        </button>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* RESULTS SECTION (Shown when result is available) */}
        {!isLoading && result && (
          <div className="space-y-8 animate-in fade-in duration-300">
            {/* Header & Disclaimer */}
            <div className="space-y-2">
              <div className="flex items-center justify-between gap-4 flex-wrap">
                <div>
                  <span className="text-xs font-bold uppercase tracking-wider text-blue-600 bg-blue-50 px-3 py-1 rounded-full border border-blue-100">
                    Laporan Hasil
                  </span>
                  <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight mt-2">
                    Hasil Analisis Lowongan
                  </h1>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={handleReset}
                    className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg border border-slate-200 bg-white text-slate-700 text-xs font-semibold hover:bg-slate-50 transition-colors shadow-xs"
                  >
                    <RotateCcw className="w-3.5 h-3.5" />
                    <span>Cek Lainnya</span>
                  </button>
                  <button
                    type="button"
                    onClick={handlePrint}
                    className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-slate-900 text-white text-xs font-semibold hover:bg-slate-800 transition-colors shadow-xs"
                  >
                    <Printer className="w-3.5 h-3.5" />
                    <span>Cetak / PDF</span>
                  </button>
                </div>
              </div>

              {/* Disclaimer Notice */}
              <div className="p-3.5 rounded-xl bg-slate-100/70 border border-slate-200/80 text-xs text-slate-600 leading-relaxed">
                <strong>Disclaimer: </strong>
                {result.disclaimer}
              </div>
            </div>

            {/* Top Grid: Risk Meter Gauge + Executive Summary */}
            <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-stretch">
              {/* Left Column: Risk Meter */}
              <div className="md:col-span-5 flex flex-col">
                <RiskGauge
                  score={result.risk_score}
                  level={result.risk_level}
                  color={result.risk_color}
                  size={260}
                />
              </div>

              {/* Right Column: Ringkasan Hasil */}
              <div className="md:col-span-7 bg-white rounded-2xl border border-slate-200 p-6 flex flex-col justify-between shadow-xs">
                <div>
                  <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-3">
                    <h3 className="font-bold text-slate-900 text-base">
                      Ringkasan
                    </h3>
                    <span className="text-[11px] font-semibold text-slate-400">
                      ID: #{result.id || "TEMP"}
                    </span>
                  </div>

                  <p className="text-sm text-slate-700 leading-relaxed mb-5">
                    {result.summary}
                  </p>

                  {/* Summary Metric Badges */}
                  <div className="grid grid-cols-2 gap-3 pt-2">
                    <div className="p-3 rounded-xl bg-slate-50 border border-slate-200">
                      <span className="text-[11px] text-slate-500 font-semibold uppercase tracking-wider block">
                        Total Indikator
                      </span>
                      <span className="text-xl font-extrabold text-slate-900 mt-0.5 block">
                        {result.indicators_detected_count} terdeteksi
                      </span>
                    </div>

                    <div className="p-3 rounded-xl bg-amber-50/50 border border-amber-200">
                      <span className="text-[11px] text-amber-700 font-semibold uppercase tracking-wider block">
                        Prioritas Konfirmasi
                      </span>
                      <span className="text-xl font-extrabold text-amber-800 mt-0.5 block">
                        {result.indicators_attention_count + result.indicators_high_count} perlu diverifikasi
                      </span>
                    </div>
                  </div>
                </div>

                {/* Extracted text preview */}
                {(result.extracted_text || result.raw_input) && (
                  <div className="mt-5 pt-4 border-t border-slate-100">
                    <div className="mb-2">
                      <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500">
                        Teks Hasil OCR / Ekstraksi
                      </span>
                    </div>
                    <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 text-slate-700 text-xs font-mono max-h-48 overflow-y-auto whitespace-pre-wrap leading-relaxed">
                      {result.extracted_text || result.raw_input}
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* SECTION INDIKATOR YANG TERDETEKSI (10 CARDS) */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-bold text-slate-900 tracking-tight">
                    Indikator yang Terdeteksi
                  </h2>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Pemeriksaan menyeluruh terhadap 10 indikator risiko digital. Klik indikator untuk melihat bukti dan alasan.
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {result.indicators.map((ind) => (
                  <IndicatorCard
                    key={ind.code}
                    indicator={ind}
                    onSelect={(i) => setSelectedIndicator(i)}
                  />
                ))}
              </div>
            </div>

            {/* SECTION REKOMENDASI VERIFIKASI (INTERACTIVE CHECKLIST) */}
            <VerificationChecklist steps={result.verification_steps} />

            {/* BOTTOM ACTION BUTTONS */}
            <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-6 border-t border-slate-200">
              <div className="flex items-center gap-3 w-full sm:w-auto">
                <button
                  type="button"
                  onClick={handleReset}
                  className="flex-1 sm:flex-none px-6 py-3 rounded-xl bg-slate-900 text-white font-semibold text-sm hover:bg-blue-600 transition-colors shadow-xs"
                >
                  Analisis Lowongan Lain
                </button>
                <Link
                  href="/"
                  className="flex-1 sm:flex-none px-6 py-3 rounded-xl border border-slate-200 bg-white text-slate-700 font-semibold text-sm hover:bg-slate-50 transition-colors text-center"
                >
                  Kembali ke Beranda
                </Link>
              </div>

              <button
                type="button"
                onClick={handlePrint}
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl border border-slate-200 bg-white text-slate-600 font-medium text-xs hover:bg-slate-50 transition-colors"
              >
                <Printer className="w-4 h-4" />
                <span>Unduh Hasil Analisis (PDF / Cetak)</span>
              </button>
            </div>
          </div>
        )}

        {/* Modal for In-depth Indicator Details */}
        <IndicatorModal
          indicator={selectedIndicator}
          onClose={() => setSelectedIndicator(null)}
        />
      </main>

      <Footer />
    </div>
  );
}
