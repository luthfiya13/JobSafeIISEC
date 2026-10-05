"use client";

import React, { useEffect, useState } from "react";
import { Check, Loader2, Circle } from "lucide-react";

interface LoadingAnalysisProps {
  onComplete?: () => void;
  inputType?: "text" | "photo" | "link";
}

const STEPS = [
  "Membaca informasi lowongan",
  "Mengekstraksi informasi penting",
  "Menganalisis indikator risiko",
  "Menghitung Risk Score",
  "Menyiapkan rekomendasi verifikasi"
];

export default function LoadingAnalysis({ onComplete, inputType = "text" }: LoadingAnalysisProps) {
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [isTakingLong, setIsTakingLong] = useState(false);

  useEffect(() => {
    // Progressive cadence
    const timeouts = [
      setTimeout(() => setCurrentStepIndex(1), 400),
      setTimeout(() => setCurrentStepIndex(2), 850),
      setTimeout(() => setCurrentStepIndex(3), 1350),
      setTimeout(() => setCurrentStepIndex(4), 1800),
      setTimeout(() => setIsTakingLong(true), 10000),
      setTimeout(() => {
        if (onComplete) onComplete();
      }, 2300),
    ];

    return () => {
      timeouts.forEach(clearTimeout);
    };
  }, [onComplete]);

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

        {/* 5 Progress Steps */}
        <div className="space-y-3.5 text-left border-t border-slate-100 pt-6">
          {STEPS.map((step, idx) => {
            const isDone = idx < currentStepIndex;
            const isCurrent = idx === currentStepIndex;

            return (
              <div
                key={step}
                className={`flex items-center gap-3 text-sm transition-all duration-300 ${
                  isDone
                    ? "text-slate-800 font-medium"
                    : isCurrent
                    ? "text-blue-600 font-semibold"
                    : "text-slate-400"
                }`}
              >
                {/* Step indicator symbol */}
                <div className="w-6 h-6 rounded-full flex items-center justify-center shrink-0">
                  {isDone ? (
                    <div className="w-5 h-5 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center">
                      <Check className="w-3.5 h-3.5 stroke-[2.5]" />
                    </div>
                  ) : isCurrent ? (
                    <div className="w-5 h-5 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center animate-pulse">
                      <div className="w-2.5 h-2.5 rounded-full bg-blue-600" />
                    </div>
                  ) : (
                    <Circle className="w-4 h-4 text-slate-300 stroke-[1.5]" />
                  )}
                </div>

                <span>{step}</span>
              </div>
            );
          })}
        </div>

        {isTakingLong && inputType === "photo" && (
          <p className="mt-4 text-xs text-slate-500" aria-live="polite">
            OCR foto masih diproses. Gambar beresolusi besar bisa memerlukan waktu lebih lama.
          </p>
        )}

        <div className="mt-8 pt-4 border-t border-slate-100">
          <span className="text-[11px] text-slate-400">
            Penilaian objektif berbasis indikator tanpa bias mutlak
          </span>
        </div>
      </div>
    </div>
  );
}
