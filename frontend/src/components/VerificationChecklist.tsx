"use client";

import React, { useState } from "react";
import { CheckSquare, Square, ShieldCheck } from "lucide-react";
import { VerificationStep } from "@/lib/api";

interface VerificationChecklistProps {
  steps: VerificationStep[];
}

export default function VerificationChecklist({ steps }: VerificationChecklistProps) {
  const [checkedIds, setCheckedIds] = useState<Record<string, boolean>>({});

  const toggleCheck = (id: string) => {
    setCheckedIds((prev) => ({
      ...prev,
      [id]: !prev[id],
    }));
  };

  const totalSteps = steps.length;
  const completedCount = Object.values(checkedIds).filter(Boolean).length;
  const progressPercent = totalSteps > 0 ? Math.round((completedCount / totalSteps) * 100) : 0;

  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-5 border-b border-slate-100">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-1 rounded-md bg-blue-50 text-blue-600">
              <ShieldCheck className="w-4 h-4" />
            </span>
            <h3 className="text-lg font-bold text-slate-900 tracking-tight">
              Sebelum Melamar, Lakukan Verifikasi
            </h3>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Centang langkah verifikasi berikut secara mandiri untuk memastikan keamanan lamaran Anda.
          </p>
        </div>

        {/* Progress Counter */}
        <div className="flex flex-col items-end shrink-0">
          <span className="text-xs font-semibold text-slate-700">
            {completedCount} dari {totalSteps} Ditandai selesai ({progressPercent}%)
          </span>
          <div className="w-36 h-2 bg-slate-100 rounded-full mt-1.5 overflow-hidden">
            <div
              className="h-full bg-blue-600 rounded-full transition-all duration-300"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
        </div>
      </div>

      {/* Checklist items */}
      <div className="mt-5 space-y-3">
        {steps.map((step) => {
          const isChecked = !!checkedIds[step.id];

          return (
            <div
              key={step.id}
              onClick={() => toggleCheck(step.id)}
              className={`flex items-start gap-3.5 p-3.5 rounded-xl border transition-all cursor-pointer ${
                isChecked
                  ? "bg-blue-50/40 border-blue-200 text-slate-900"
                  : "bg-slate-50/50 border-slate-200/80 hover:bg-slate-50 hover:border-slate-300 text-slate-700"
              }`}
            >
              <button
                type="button"
                className="mt-0.5 text-blue-600 focus:outline-hidden shrink-0"
                aria-label={`Centang ${step.title}`}
              >
                {isChecked ? (
                  <CheckSquare className="w-5 h-5 text-blue-600 fill-blue-50" />
                ) : (
                  <Square className="w-5 h-5 text-slate-400" />
                )}
              </button>

              <div className="flex-1">
                <h4
                  className={`text-sm font-semibold leading-snug transition-colors ${
                    isChecked ? "text-slate-900 line-through decoration-slate-400 text-opacity-80" : "text-slate-900"
                  }`}
                >
                  {step.title}
                </h4>
                <p className="text-xs text-slate-500 mt-0.5 leading-relaxed">
                  {step.desc}
                </p>
              </div>
            </div>
          );
        })}
      </div>

      <p className="mt-5 text-[11px] text-slate-500">
        Catatan: centang ini hanya mencatat tindakan Anda sendiri. JOBSAFE tidak mengklaim telah memverifikasi perusahaan atau kontak tersebut.
      </p>
    </div>
  );
}
