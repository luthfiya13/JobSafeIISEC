import { NextResponse } from "next/server";

export async function GET() {
  return NextResponse.json({
    total_analyses: 8,
    risk_low: 2,
    risk_medium: 4,
    risk_high: 2,
    distribution: {
      low_pct: 25.0,
      med_pct: 50.0,
      high_pct: 25.0
    },
    top_indicators: [
      { code: "R1", count: 4 },
      { code: "R6", count: 3 },
      { code: "R3", count: 2 },
      { code: "R8", count: 2 },
      { code: "R2", count: 1 },
      { code: "R7", count: 1 }
    ],
    recent_analyses: [
      {
        id: 8,
        input_type: "text",
        input_preview: "Dicari Admin Online Like Video TikTok & YouTube. Komisi harian 500rb - 1jt. Wajib deposit awal...",
        risk_score: 85,
        risk_level: "RISIKO TINGGI",
        level_code: "HIGH",
        detected_count: 3,
        created_at: new Date().toISOString()
      },
      {
        id: 7,
        input_type: "text",
        input_preview: "Dibutuhkan Data Entry Remote Part Time. Kirimkan foto KTP dan buku tabungan via WA...",
        risk_score: 45,
        risk_level: "RISIKO SEDANG",
        level_code: "MEDIUM",
        detected_count: 2,
        created_at: new Date(Date.now() - 3600000).toISOString()
      },
      {
        id: 6,
        input_type: "link",
        input_preview: "https://karir-bumn-rekrutmen.id/panggilan-interview-surat-resmi",
        risk_score: 75,
        risk_level: "RISIKO TINGGI",
        level_code: "HIGH",
        detected_count: 2,
        created_at: new Date(Date.now() - 7200000).toISOString()
      },
      {
        id: 5,
        input_type: "text",
        input_preview: "Lowongan Junior Software Engineer (React/Next.js) di PT Solusi Teknologi Digital...",
        risk_score: 10,
        risk_level: "RISIKO RENDAH",
        level_code: "LOW",
        detected_count: 0,
        created_at: new Date(Date.now() - 14400000).toISOString()
      }
    ]
  });
}
