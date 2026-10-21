"use client";

import React, { useEffect, useState, useId } from "react";
import { ShieldCheck, AlertTriangle, AlertOctagon } from "lucide-react";

interface RiskGaugeProps {
  score: number; // 0 to 100
  level: string; // "RISIKO RENDAH", "RISIKO SEDANG", "RISIKO TINGGI"
  color: "green" | "amber" | "red";
  thresholds?: { low_max: number; high_min: number };
  size?: number;
}

export default function RiskGauge({ score, level, color, thresholds, size = 280 }: RiskGaugeProps) {
  const [animatedScore, setAnimatedScore] = useState(0);
  const gaugeId = useId().replace(/:/g, "-");

  useEffect(() => {
    const timer = setTimeout(() => {
      setAnimatedScore(Math.max(0, Math.min(100, Math.round(score))));
    }, 150);
    return () => clearTimeout(timer);
  }, [score]);

  // Color mappings adhering strictly to green -> amber -> red risk spectrum with light-theme badges
  const colorMap = {
    green: {
      stroke: "#10b981", // Emerald 500
      strokeStart: "#059669",
      strokeEnd: "#34d399",
      needleTip: "#059669",
      glow: "rgba(16, 185, 129, 0.35)",
      ambientGlow: "rgba(16, 185, 129, 0.08)",
      text: "text-emerald-700",
      bgBadge: "bg-emerald-50 border-emerald-200 text-emerald-800",
      icon: ShieldCheck,
      rangeText: `🟢 Skor 0–${thresholds?.low_max ?? 24}: risiko rendah; tidak berarti aman mutlak`,
    },
    amber: {
      stroke: "#f59e0b", // Amber 500
      strokeStart: "#d97706",
      strokeEnd: "#fbbf24",
      needleTip: "#d97706",
      glow: "rgba(245, 158, 11, 0.35)",
      ambientGlow: "rgba(245, 158, 11, 0.08)",
      text: "text-amber-700",
      bgBadge: "bg-amber-50 border-amber-200 text-amber-800",
      icon: AlertTriangle,
      rangeText: `🟡 Skor ${(thresholds?.low_max ?? 24) + 1}–${(thresholds?.high_min ?? 60) - 1}: perlu klarifikasi dan verifikasi`,
    },
    red: {
      stroke: "#ef4444", // Red 500
      strokeStart: "#dc2626",
      strokeEnd: "#f87171",
      needleTip: "#dc2626",
      glow: "rgba(239, 68, 68, 0.4)",
      ambientGlow: "rgba(239, 68, 68, 0.08)",
      text: "text-red-700",
      bgBadge: "bg-red-50 border-red-200 text-red-800",
      icon: AlertOctagon,
      rangeText: `🔴 Skor ${thresholds?.high_min ?? 60}–100: risiko tinggi; verifikasi sebelum melanjutkan`,
    },
  };

  const currentTheme = colorMap[color] || colorMap.amber;
  const IconComponent = currentTheme.icon;
  const riskSymbol =
    level === "RISIKO TINGGI"
      ? "🔴"
      : level === "RISIKO SEDANG"
        ? "🟡"
        : "🟢";

  // Ookla speedometer geometry:
  // Center at (150, 130), Radius = 98.
  // 240-degree open horseshoe gauge: starts at 150° (bottom-left) and ends at 390° (30°, bottom-right).
  const cx = 150;
  const cy = 130;
  const radius = 98;
  const arcSweep = 240;
  const startAngle = 150;
  const circumference = 2 * Math.PI * radius;
  const totalArc = circumference * (arcSweep / 360); // ~410.5
  const strokeDashoffset = totalArc - (animatedScore / 100) * totalArc;

  // Needle angle sweeps from 150° (at score 0) to 390° (at score 100)
  const needleAngle = startAngle + (animatedScore / 100) * arcSweep;

  // Generate graduation scale ticks (every 5 units, major at 0, 25, 50, 75, 100)
  const ticks = [];
  for (let i = 0; i <= 20; i++) {
    const val = i * 5;
    const isMajor = i % 5 === 0;
    const angleDeg = startAngle + (val / 100) * arcSweep;
    const angleRad = (angleDeg * Math.PI) / 180;
    const cosA = Math.cos(angleRad);
    const sinA = Math.sin(angleRad);

    const rInner = isMajor ? 78 : 82;
    const rOuter = 86;
    const x1 = cx + rInner * cosA;
    const y1 = cy + rInner * sinA;
    const x2 = cx + rOuter * cosA;
    const y2 = cy + rOuter * sinA;

    // Label coordinates for major scale numbers (0, 25, 50, 75, 100)
    let labelPos = null;
    if (isMajor) {
      const rLabel = 65;
      labelPos = {
        x: cx + rLabel * cosA,
        y: cy + rLabel * sinA,
        text: val.toString(),
      };
    }

    ticks.push({
      key: `tick-${val}`,
      isMajor,
      x1,
      y1,
      x2,
      y2,
      labelPos,
    });
  }

  return (
    <div className="flex flex-col items-center justify-center p-6 bg-white rounded-2xl border border-slate-200 shadow-xs relative overflow-hidden text-slate-800 transition-all duration-300">
      {/* Background ambient subtle glow */}
      <div
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 rounded-full blur-3xl pointer-events-none transition-colors duration-700 opacity-60 print:hidden"
        style={{ backgroundColor: currentTheme.ambientGlow }}
      />

      {/* Header Label */}
      <div className="text-center mb-1 relative z-10">
        <span className="text-[11px] font-bold uppercase tracking-widest text-slate-500">
          Tingkat Risiko Terdeteksi
        </span>
      </div>

      {/* SVG Ookla Speedometer Gauge */}
      <div
        className="relative flex items-center justify-center my-1 select-none z-10"
        style={{ width: "100%", maxWidth: size }}
      >
        <svg
          viewBox="0 0 300 245"
          className="w-full h-auto overflow-visible"
        >
          <defs>
            {/* White / Light dial face subtle radial gradient */}
            <radialGradient id={`dialBg-${gaugeId}`} cx="50%" cy="45%" r="55%">
              <stop offset="0%" stopColor="#ffffff" />
              <stop offset="70%" stopColor="#f8fafc" />
              <stop offset="100%" stopColor="#f1f5f9" />
            </radialGradient>

            {/* Active arc gradient */}
            <linearGradient id={`arcGrad-${gaugeId}`} x1="0%" y1="100%" x2="100%" y2="0%">
              <stop offset="0%" stopColor={currentTheme.strokeStart} />
              <stop offset="60%" stopColor={currentTheme.stroke} />
              <stop offset="100%" stopColor={currentTheme.strokeEnd} />
            </linearGradient>

            {/* Needle gradient from center pivot to tip */}
            <linearGradient id={`needleGrad-${gaugeId}`} x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="rgba(71, 85, 105, 0.25)" />
              <stop offset="45%" stopColor="rgba(51, 65, 85, 0.65)" />
              <stop offset="85%" stopColor={currentTheme.stroke} stopOpacity="0.9" />
              <stop offset="100%" stopColor={currentTheme.needleTip} stopOpacity="1" />
            </linearGradient>

            {/* Glowing neon drop-shadow filters */}
            <filter id={`arcGlow-${gaugeId}`} x="-20%" y="-20%" width="140%" height="140%">
              <feDropShadow dx="0" dy="0" stdDeviation="3.5" floodColor={currentTheme.stroke} floodOpacity="0.4" />
            </filter>
            <filter id={`needleGlow-${gaugeId}`} x="-30%" y="-30%" width="160%" height="160%">
              <feDropShadow dx="0" dy="0" stdDeviation="2.5" floodColor={currentTheme.stroke} floodOpacity="0.5" />
            </filter>
          </defs>

          {/* Instrument bezel outer rim */}
          <circle
            cx={cx}
            cy={cy}
            r="124"
            fill={`url(#dialBg-${gaugeId})`}
            stroke="#e2e8f0"
            strokeWidth="2"
          />

          {/* Inner subtle rim guide line */}
          <circle
            cx={cx}
            cy={cy}
            r="115"
            fill="none"
            stroke="#f1f5f9"
            strokeWidth="1.5"
          />

          {/* Inactive Track Arc (light slate modern channel) */}
          <circle
            cx={cx}
            cy={cy}
            r={radius}
            fill="none"
            stroke="#e2e8f0"
            strokeWidth="15"
            strokeDasharray={`${totalArc} ${circumference}`}
            strokeDashoffset="0"
            strokeLinecap="round"
            transform={`rotate(${startAngle} ${cx} ${cy})`}
          />

          {/* Active Progress Arc (glowing colored gradient) */}
          <circle
            cx={cx}
            cy={cy}
            r={radius}
            fill="none"
            stroke={`url(#arcGrad-${gaugeId})`}
            strokeWidth="15"
            strokeDasharray={`${totalArc} ${circumference}`}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            transform={`rotate(${startAngle} ${cx} ${cy})`}
            filter={`url(#arcGlow-${gaugeId})`}
            style={{
              transition: "stroke-dashoffset 1.4s cubic-bezier(0.34, 1.3, 0.64, 1)",
            }}
          />

          {/* Graduation Scale Ticks & Numbers */}
          {ticks.map((t) => (
            <g key={t.key}>
              <line
                x1={t.x1}
                y1={t.y1}
                x2={t.x2}
                y2={t.y2}
                stroke={t.isMajor ? "#64748b" : "#cbd5e1"}
                strokeWidth={t.isMajor ? "2" : "1"}
                strokeLinecap="round"
              />
              {t.labelPos && (
                <text
                  x={t.labelPos.x}
                  y={t.labelPos.y}
                  fill="#475569"
                  fontSize="10"
                  fontWeight="700"
                  fontFamily="system-ui, -apple-system, sans-serif"
                  textAnchor="middle"
                  dominantBaseline="central"
                >
                  {t.labelPos.text}
                </text>
              )}
            </g>
          ))}

          {/* Ookla-Style Tapered Needle (Pivots smoothly from center cx, cy) */}
          <g
            transform={`rotate(${needleAngle} ${cx} ${cy})`}
            style={{
              transition: "transform 1.4s cubic-bezier(0.34, 1.25, 0.64, 1)",
            }}
          >
            {/* Tapered needle pointer */}
            <path
              d={`M ${cx} ${cy - 4} L ${cx + 80} ${cy - 1.2} L ${cx + 84} ${cy} L ${cx + 80} ${cy + 1.2} L ${cx} ${cy + 4} Z`}
              fill={`url(#needleGrad-${gaugeId})`}
              filter={`url(#needleGlow-${gaugeId})`}
            />
          </g>

          {/* Needle Center Hub Cap (Metallic bezel disc) */}
          <circle
            cx={cx}
            cy={cy}
            r="13"
            fill="#f1f5f9"
            stroke="#cbd5e1"
            strokeWidth="2"
          />
          <circle
            cx={cx}
            cy={cy}
            r="8"
            fill="#334155"
          />
          <circle
            cx={cx}
            cy={cy}
            r="3.5"
            fill={currentTheme.stroke}
            style={{
              transition: "fill 0.5s ease",
            }}
          />

          {/* Digital Readout inside bottom cavity (Ookla speedometer style) */}
          <text
            x={cx}
            y={cy + 45}
            fill="#64748b"
            fontSize="9"
            fontWeight="700"
            letterSpacing="2"
            textAnchor="middle"
            className="uppercase"
          >
            SKOR RISIKO
          </text>
          <text
            x={cx}
            y={cy + 78}
            fill={currentTheme.stroke}
            fontSize="38"
            fontWeight="900"
            fontFamily="system-ui, -apple-system, sans-serif"
            textAnchor="middle"
            style={{
              transition: "fill 0.5s ease",
            }}
          >
            {animatedScore}
          </text>
          <text
            x={cx}
            y={cy + 94}
            fill="#94a3b8"
            fontSize="10"
            fontWeight="700"
            textAnchor="middle"
          >
            / 100
          </text>
        </svg>
      </div>

      {/* Level Status Badge (Bottom of the gauge) */}
      <div className="mt-1 relative z-10">
        <span
          className={`inline-flex items-center gap-1.5 px-3.5 py-1 rounded-full text-xs font-bold border tracking-wider uppercase transition-all duration-300 ${currentTheme.bgBadge}`}
        >
          <IconComponent className="w-3.5 h-3.5" />
          <span aria-hidden="true">{riskSymbol}</span>
          <span>{level}</span>
        </span>
      </div>

      {/* Range description & advisory disclaimer */}
      <div className="text-center mt-3 pt-3 border-t border-slate-100 w-full relative z-10">
        <p className="text-xs text-slate-600 font-medium">
          {currentTheme.rangeText}
        </p>
        <p className="text-[11px] text-slate-400 mt-1">
          Skor indikasi, bukan persentase kepastian penipuan.
        </p>
      </div>
    </div>
  );
}

