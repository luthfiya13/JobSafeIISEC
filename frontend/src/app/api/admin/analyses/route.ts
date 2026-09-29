import { NextResponse } from "next/server";

const mockAnalyses = [
  {
    id: 1,
    input_type: "text",
    input_preview: "Dicari Admin Online Like Video TikTok & YouTube. Komisi harian 500rb - 1jt. Wajib deposit awal Rp250.000...",
    risk_score: 85,
    risk_level: "RISIKO TINGGI",
    level_code: "HIGH",
    indicators: [{ code: "R1", name: "Biaya di Awal" }, { code: "R2", name: "Imbalan Tidak Wajar" }, { code: "R6", name: "Skema Tugas Berantai" }],
    detected_count: 3,
    summary: "Ditemukan indikator kuat skema tugas berantai like/subscribe dengan syarat deposit uang di awal.",
    created_at: new Date().toISOString()
  },
  {
    id: 2,
    input_type: "link",
    input_preview: "https://karir-bumn-rekrutmen.id/panggilan-interview-surat-resmi",
    risk_score: 75,
    risk_level: "RISIKO TINGGI",
    level_code: "HIGH",
    indicators: [{ code: "R7", name: "Perjalanan/Akomodasi Wajib" }, { code: "R4", name: "Identitas Perusahaan Tidak Jelas" }],
    detected_count: 2,
    summary: "Mengarah pada modus penipuan panggilan tes luar kota dengan kewajiban reservasi tiket travel fiktif.",
    created_at: new Date(Date.now() - 3600000).toISOString()
  },
  {
    id: 3,
    input_type: "text",
    input_preview: "Dibutuhkan Data Entry Remote Part Time. Kirimkan foto KTP depan belakang dan buku tabungan via WhatsApp admin...",
    risk_score: 45,
    risk_level: "RISIKO SEDANG",
    level_code: "MEDIUM",
    indicators: [{ code: "R3", name: "Permintaan Dokumen Sensitif" }, { code: "R8", name: "Kanal Komunikasi Tidak Resmi" }],
    detected_count: 2,
    summary: "Permintaan dokumen identitas pribadi di tahap awal melalui WhatsApp tanpa saluran resmi korporat.",
    created_at: new Date(Date.now() - 7200000).toISOString()
  },
  {
    id: 4,
    input_type: "text",
    input_preview: "Lowongan Junior Software Engineer (React/Next.js) di PT Solusi Teknologi Digital. Gaji kompetitif sesuai pengalaman.",
    risk_score: 10,
    risk_level: "RISIKO RENDAH",
    level_code: "LOW",
    indicators: [],
    detected_count: 0,
    summary: "Format dan kualifikasi lowongan terlihat standar dan profesional, tidak ditemukan tanda-tanda risiko signifikan.",
    created_at: new Date(Date.now() - 14400000).toISOString()
  }
];

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url);
  const q = searchParams.get("q")?.toLowerCase();
  const level = searchParams.get("level")?.toUpperCase();

  let filtered = [...mockAnalyses];

  if (level && level !== "ALL") {
    filtered = filtered.filter((item) => item.level_code === level);
  }

  if (q) {
    filtered = filtered.filter(
      (item) =>
        item.input_preview.toLowerCase().includes(q) ||
        item.summary.toLowerCase().includes(q)
    );
  }

  return NextResponse.json({
    items: filtered,
    count: filtered.length
  });
}
