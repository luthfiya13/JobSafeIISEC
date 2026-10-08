"use client";

import React, { useEffect, useState } from "react";
import { Loader2 } from "lucide-react";

interface LoadingAnalysisProps {
  inputType?: "text" | "photo" | "link";
}

export default function LoadingAnalysis({ inputType = "text" }: LoadingAnalysisProps) {
  const [isTakingLong, setIsTakingLong] = useState(false);

  useEffect(() => {
    // The API currently exposes one atomic analysis request, so do not claim
    // that internal stages completed based on elapsed time.
    const timeout = setTimeout(() => setIsTakingLong(true), 10000);
    return () => clearTimeout(timeout);
  }, []);

  return (
    <div className="min-h-[500px] flex items-center justify-center p-6">
      <div className="bg-white rounded-2xl border border-slate-200 p-8 sm:p-10 max-w-md w-full shadow-xs text-center">
        {/* Animated icon */}
        <div className="w-16 h-16 rounded-2xl bg-blue-50 border border-blue-100 flex items-center justify-center mx-auto mb-5 text-blue-600 relative">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
          <div className="absolute inset-0 rounded-2xl animate-ping bg-blue-100 opacity-20 pointer-events-none" />
        </div>

        <h3 className="text-xl font-bold text-slate-900 tracking-tight mb-1">
          Sedang menganalisis lowongan...
        </h3>
        <p className="text-xs text-slate-500 mb-8">
          {inputType === "photo"
            ? "Mengekstraksi teks OCR dari screenshot dan mencocokkan indikator..."
            : inputType === "link"
            ? "Mengambil data konten tautan web dan memindai tanda risiko..."
            : "Sistem sedang memindai pola teks terhadap 10 indikator risiko digital..."}
        </p>

        <div className="border-t border-slate-100 pt-6 text-sm font-medium text-blue-700" aria-live="polite">
          {inputType === "photo" ? "OCR berjalan di browser, kemudian teks dikirim ke model." :
            inputType === "link" ? "Backend sedang mengambil teks halaman dan menunggu model." :
              "Permintaan sedang diproses oleh model JOBSAFE v3."}
        </div>

        {isTakingLong && inputType === "photo" && (
          <p className="mt-4 text-xs text-slate-500" aria-live="polite">
            OCR foto masih diproses. Gambar beresolusi besar bisa memerlukan waktu lebih lama.
          </p>
        )}

        <div className="mt-8 pt-4 border-t border-slate-100">
          <span className="text-[11px] text-slate-400">
            Status menunggu respons layanan analisis
          </span>
        </div>
      </div>
    </div>
  );
}
