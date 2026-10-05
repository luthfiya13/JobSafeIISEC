"use client";

import React, { useEffect, useState } from "react";
import { ShieldCheck, AlertTriangle, AlertOctagon } from "lucide-react";

interface RiskGaugeProps {
  score: number; // 0 to 100
  level: string; // "RISIKO RENDAH", "RISIKO SEDANG", "RISIKO TINGGI"
  color: "green" | "amber" | "red";
  size?: number;
}

export default function RiskGauge({ score, level, color, size = 260 }: RiskGaugeProps) {
  const [animatedScore, setAnimatedScore] = useState(0);

  useEffect(() => {
    const timer = setTimeout(() => {
      setAnimatedScore(score);
    }, 150);
    return () => clearTimeout(timer);
  }, [score]);

  // Color mappings
  const colorMap = {
    green: {
      stroke: "#16a34a",
      bgStroke: "#dcfce7",
      text: "text-emerald-700",
      bgBadge: "bg-emerald-50 border-emerald-200 text-emerald-800",
      glow: "rgba(22, 163, 74, 0.15)",
      icon: ShieldCheck,
      rangeText: "🟢 Skor 0–4: Risiko rendah"
    },
    amber: {
      stroke: "#f59e0b",
      bgStroke: "#fef3c7",
      text: "text-amber-700",
      bgBadge: "bg-amber-50 border-amber-200 text-amber-800",
      glow: "rgba(245, 158, 11, 0.15)",
      icon: AlertTriangle,
      rangeText: "🟡 Skor 5–39 tanpa Hard Flag: Risiko sedang"
    },
    red: {
      stroke: "#dc2626",
      bgStroke: "#fee2e2",
      text: "text-red-700",
      bgBadge: "bg-red-50 border-red-200 text-red-800",
      glow: "rgba(220, 38, 38, 0.18)",
      icon: AlertOctagon,
      rangeText: "🔴 Hard Flag atau skor ≥ 40: Risiko tinggi"
    }
  };

  const currentTheme = colorMap[color] || colorMap.amber;
  const IconComponent = currentTheme.icon;
  const riskSymbol = level === "RISIKO TINGGI"
    ? "🔴"
    : level === "RISIKO SEDANG"
      ? "🟡"
      : "🟢";

  // Arc calculation for semi/gauge circle (240 degrees arc)
  const radius = 95;
  const circumference = 2 * Math.PI * radius;
  // Use a 240-degree open gauge for elegant dashboard look
  const totalArc = circumference * (240 / 360);
  const strokeDashoffset = totalArc - (animatedScore / 100) * totalArc;

  return (
    <div className="flex flex-col items-center justify-center p-6 bg-white rounded-2xl border border-slate-200 shadow-xs relative overflow-hidden">
      {/* Subtle background ambient glow */}
      <div
        className="absolute -top-12 -right-12 w-48 h-48 rounded-full blur-3xl pointer-events-none transition-colors duration-700"
        style={{ backgroundColor: currentTheme.glow }}
      />

      <div className="text-center mb-1">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
          Tingkat Risiko Terdeteksi
        </span>
      </div>

      {/* SVG Meter Gauge */}
      <div className="relative flex items-center justify-center my-2" style={{ width: size, height: size * 0.85 }}>
        <svg
          width={size}
          height={size * 0.85}
          viewBox="0 0 240 210"
          className="transform rotate-0"
        >
          {/* Background track */}
          <circle
            cx="120"
            cy="125"
            r={radius}
            fill="none"
            stroke="#f1f5f9"
            strokeWidth="14"
            strokeDasharray={totalArc}
            strokeDashoffset="0"
            strokeLinecap="round"
            transform="rotate(150 120 125)"
          />

          {/* Active progress arc */}
          <circle
            cx="120"
            cy="125"
            r={radius}
            fill="none"
            stroke={currentTheme.stroke}
            strokeWidth="14"
            strokeDasharray={totalArc}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            transform="rotate(150 120 125)"
            style={{
              transition: "stroke-dashoffset 1.2s cubic-bezier(0.34, 1.56, 0.64, 1)",
            }}
          />

          {/* Dial ticks */}
          <text x="35" y="185" fill="#94a3b8" fontSize="10" fontWeight="600" textAnchor="middle">0</text>
          <text x="85" y="45" fill="#94a3b8" fontSize="10" fontWeight="600" textAnchor="middle">5</text>
          <text x="155" y="45" fill="#94a3b8" fontSize="10" fontWeight="600" textAnchor="middle">40</text>
          <text x="205" y="185" fill="#94a3b8" fontSize="10" fontWeight="600" textAnchor="middle">100</text>
        </svg>

        {/* Center Content */}
        <div className="absolute inset-0 flex flex-col items-center justify-center pt-8 pointer-events-none">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-widest">
            Risk Score
          </span>
          <div className="flex items-baseline gap-1 mt-0.5">
            <span
              className="text-5xl font-extrabold tracking-tight"
              style={{ color: currentTheme.stroke }}
            >
              {animatedScore}
            </span>
            <span className="text-slate-400 font-semibold text-lg">/ 100</span>
          </div>
          <div className="mt-2">
            <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold border tracking-wide uppercase ${currentTheme.bgBadge}`}>
              <IconComponent className="w-3.5 h-3.5" />
              <span aria-hidden="true">{riskSymbol}</span>
              <span>{level}</span>
            </span>
          </div>
        </div>
      </div>

      {/* Range description */}
      <div className="text-center mt-2">
        <p className="text-xs text-slate-500 font-medium">
          {currentTheme.rangeText}
        </p>
      </div>
    </div>
  );
}
