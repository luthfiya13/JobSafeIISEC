"use client";

import React from "react";
import {
  CreditCard,
  DollarSign,
  FileText,
  Building2,
  HelpCircle,
  Layers,
  Plane,
  MessageCircle,
  Globe,
  Clock,
  CheckCircle2,
  AlertTriangle,
  AlertOctagon,
  ChevronRight,
  Quote
} from "lucide-react";
import { IndicatorItem } from "@/lib/api";

interface IndicatorCardProps {
  indicator: IndicatorItem;
  onSelect: (ind: IndicatorItem) => void;
}

export const INDICATOR_ICONS: Record<string, React.ElementType> = {
  R1: CreditCard,
  R2: DollarSign,
  R3: FileText,
  R4: Building2,
  R5: HelpCircle,
  R6: Layers,
  R7: Plane,
  R8: MessageCircle,
  R9: Globe,
  R10: Clock
};

export default function IndicatorCard({ indicator, onSelect }: IndicatorCardProps) {
  const IconComp = INDICATOR_ICONS[indicator.code] || HelpCircle;

  // Status visual variants
  const isHigh = indicator.status === "RISIKO_TINGGI";
  const isAttention = indicator.status === "PERLU_PERHATIAN";
  const isSafe = indicator.status === "TIDAK_TERDETEKSI";

  let statusBadge = (
    <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-600 border border-slate-200">
      <CheckCircle2 className="w-3 h-3 text-emerald-600" />
      ✓ Tidak terdeteksi
    </span>
  );

  let borderClass = "border-slate-200 hover:border-slate-300";
  let bgClass = "bg-white";

  if (isHigh) {
    statusBadge = (
      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-red-50 text-red-700 border border-red-200">
        <AlertOctagon className="w-3 h-3 text-red-600" />
        ! Risiko tinggi
      </span>
    );
    borderClass = "border-red-200 hover:border-red-300 bg-red-50/20";
  } else if (isAttention) {
    statusBadge = (
      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200">
        <AlertTriangle className="w-3 h-3 text-amber-600" />
        ⚠ Perlu diperhatikan
      </span>
    );
    borderClass = "border-amber-200 hover:border-amber-300 bg-amber-50/20";
  }

  return (
    <div
      onClick={() => onSelect(indicator)}
      className={`clean-card p-5 cursor-pointer transition-all duration-200 hover:shadow-sm ${borderClass} ${bgClass} flex flex-col justify-between`}
    >
      <div>
        {/* Card Header: Icon, Code, Weight, Status */}
        <div className="flex items-start justify-between gap-3 mb-3">
          <div className="flex items-center gap-3">
            <div
              className={`w-10 h-10 rounded-xl flex items-center justify-center transition-colors ${
                isHigh
                  ? "bg-red-100 text-red-700"
                  : isAttention
                  ? "bg-amber-100 text-amber-700"
                  : "bg-slate-100 text-slate-700"
              }`}
            >
              <IconComp className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
                  {indicator.code}
                </span>
                <span className="text-[11px] font-semibold text-slate-500 bg-slate-100 px-2 py-0.5 rounded-md">
                  Bobot {indicator.weight}%
                </span>
              </div>
              <h3 className="font-bold text-slate-900 text-base leading-tight mt-0.5">
                {indicator.name}
              </h3>
            </div>
          </div>
        </div>

        {/* Status Badge */}
        <div className="mb-3">{statusBadge}</div>

        {/* Description */}
        <p className="text-xs text-slate-600 leading-relaxed line-clamp-2 mb-3">
          {indicator.description}
        </p>

        {/* Detected Snippet / Evidence (if detected) */}
        {indicator.evidence && (
          <div className="mt-3 p-2.5 rounded-lg bg-slate-50 border border-slate-200 text-xs text-slate-700 flex items-start gap-2">
            <Quote className="w-3.5 h-3.5 text-slate-400 shrink-0 mt-0.5" />
            <p className="italic text-slate-800 line-clamp-2">
              {indicator.evidence}
            </p>
          </div>
        )}
      </div>

      {/* Card Footer: Detail Link */}
      <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs font-medium text-blue-600 group">
        <span>Lihat detail &amp; alasan</span>
        <ChevronRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
      </div>
    </div>
  );
}
