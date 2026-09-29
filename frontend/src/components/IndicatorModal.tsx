"use client";

import React from "react";
import {
  X,
  ShieldAlert,
  AlertTriangle,
  AlertOctagon,
  CheckCircle2,
  Quote,
  Lightbulb,
  CheckCircle
} from "lucide-react";
import { IndicatorItem } from "@/lib/api";
import { INDICATOR_ICONS } from "./IndicatorCard";

interface IndicatorModalProps {
  indicator: IndicatorItem | null;
  onClose: () => void;
}

export default function IndicatorModal({ indicator, onClose }: IndicatorModalProps) {
  if (!indicator) return null;

  const IconComp = INDICATOR_ICONS[indicator.code] || ShieldAlert;
  const isHigh = indicator.status === "RISIKO_TINGGI";
  const isAttention = indicator.status === "PERLU_PERHATIAN";

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
      {/* Backdrop click */}
      <div className="fixed inset-0" onClick={onClose} />

      {/* Modal Dialog */}
      <div className="relative bg-white rounded-2xl max-w-lg w-full p-6 shadow-xl border border-slate-200 z-10 animate-in fade-in zoom-in-95 duration-200">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
          aria-label="Tutup modal"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Header */}
        <div className="flex items-center gap-3.5 mb-5 pr-8">
          <div
            className={`w-12 h-12 rounded-xl flex items-center justify-center shrink-0 ${
              isHigh
                ? "bg-red-100 text-red-700"
                : isAttention
                ? "bg-amber-100 text-amber-700"
                : "bg-slate-100 text-slate-700"
            }`}
          >
            <IconComp className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
                {indicator.code}
              </span>
              <span className="text-xs font-semibold px-2 py-0.5 rounded-md bg-slate-100 text-slate-600">
                Bobot {indicator.weight}%
              </span>
            </div>
            <h2 className="text-xl font-bold text-slate-900 leading-snug">
              {indicator.name}
            </h2>
          </div>
        </div>

        {/* Status Box */}
        <div className="mb-4">
          <div
            className={`p-3 rounded-xl border flex items-center gap-2.5 ${
              isHigh
                ? "bg-red-50 border-red-200 text-red-800"
                : isAttention
                ? "bg-amber-50 border-amber-200 text-amber-800"
                : "bg-emerald-50 border-emerald-200 text-emerald-800"
            }`}
          >
            {isHigh ? (
              <AlertOctagon className="w-5 h-5 text-red-600 shrink-0" />
            ) : isAttention ? (
              <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0" />
            ) : (
              <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
            )}
            <div className="text-sm">
              <span className="font-bold">Status: </span>
              {indicator.status === "TIDAK_TERDETEKSI" ? (
                <span>TIDAK TERDETEKSI</span>
              ) : (
                <span>TERDETEKSI ({indicator.status_label.replace(/[!⚠✓]/g, "").trim()})</span>
              )}
            </div>
          </div>
        </div>

        {/* Bukti Teks Terdeteksi (if detected) */}
        {indicator.evidence ? (
          <div className="mb-4">
            <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
              <Quote className="w-3.5 h-3.5 text-blue-600" />
              Bukti / Bagian Teks yang Terdeteksi
            </h4>
            <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 text-sm text-slate-800 italic leading-relaxed">
              &ldquo;{indicator.evidence.replace(/^..."|"...$/g, "")}&rdquo;
            </div>
          </div>
        ) : (
          <div className="mb-4 p-3 rounded-xl bg-slate-50 border border-slate-100 text-xs text-slate-500">
            Tidak ditemukan kata kunci atau pola kalimat yang cocok dengan indikator ini pada lowongan yang diperiksa.
          </div>
        )}

        {/* Mengapa Perlu Diperhatikan */}
        <div className="mb-4">
          <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
            <Lightbulb className="w-3.5 h-3.5 text-amber-500" />
            Mengapa Perlu Diperhatikan
          </h4>
          <p className="text-sm text-slate-700 leading-relaxed bg-slate-50/60 p-3 rounded-xl border border-slate-100">
            {indicator.why_important}
          </p>
        </div>

        {/* Panduan Edukatif */}
        <div className="mb-6 p-3.5 rounded-xl bg-blue-50/70 border border-blue-100 text-xs text-blue-900 leading-relaxed">
          <span className="font-semibold block mb-0.5">Catatan Penting:</span>
          Indikator ini terdeteksi dan perlu diverifikasi lebih lanjut. Adanya indikator bukan berarti secara otomatis penipuan, namun menjadi sinyal agar Anda bersikap lebih berhati-hati sebelum menyerahkan uang atau data pribadi.
        </div>

        {/* Action Button */}
        <div className="flex justify-end">
          <button
            type="button"
            onClick={onClose}
            className="w-full sm:w-auto px-5 py-2.5 rounded-lg bg-slate-900 text-white text-sm font-medium hover:bg-slate-800 transition-colors"
          >
            Tutup
          </button>
        </div>
      </div>
    </div>
  );
}
