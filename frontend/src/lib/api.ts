export interface IndicatorItem {
  code: string;
  name: string;
  category?: string;
  weight: number;
  status: "TIDAK_TERDETEKSI" | "PERLU_PERHATIAN" | "RISIKO_TINGGI";
  status_label: string;
  status_badge: "safe" | "attention" | "high";
  description: string;
  why_important: string;
  matches_count?: number;
  evidence?: string | null;
}

export interface VerificationStep {
  id: string;
  title: string;
  desc: string;
}

export interface AnalysisResult {
  id?: number;
  risk_score: number;
  risk_level: "RISIKO RENDAH" | "RISIKO SEDANG" | "RISIKO TINGGI";
  risk_color: "green" | "amber" | "red";
  risk_theme: string;
  level_code: "LOW" | "MEDIUM" | "HIGH";
  summary: string;
  findings_summary?: string;
  preventive_advice?: string;
  indicators_detected_count: number;
  indicators_attention_count: number;
  indicators_high_count: number;
  indicators: IndicatorItem[];
  verification_steps: VerificationStep[];
  disclaimer: string;
  raw_input?: string;
  input_type?: "text" | "photo" | "link";
  extracted_text?: string;
  page_title?: string;
}

export interface AdminAnalysisRecord {
  id: number;
  input_type: "text" | "photo" | "link";
  input_preview: string;
  risk_score: number;
  risk_level: string;
  level_code: "LOW" | "MEDIUM" | "HIGH";
  detected_count: number;
  created_at: string;
  indicators?: Array<{ code?: string; name?: string }>;
  summary: string;
}

export interface AdminDashboardStats {
  total_analyses: number;
  risk_low: number;
  risk_medium: number;
  risk_high: number;
  distribution: { low_pct: number; med_pct: number; high_pct: number };
  top_indicators: Array<{ code: string; count: number }>;
  recent_analyses: AdminAnalysisRecord[];
}

export interface AdminIndicator {
  code: string;
  name: string;
  weight: number;
  hard_flag: boolean;
  is_active: boolean;
  category: string;
  description: string;
  why_important: string;
  keywords: string[];
}

export interface AdminSettings {
  site_name: string;
  threshold_low_max: number | string;
  threshold_med_max: number | string;
  threshold_high_min: number | string;
  analysis_engine_version: string;
  maintenance_mode: boolean | string;
}

export interface PublicIndicator {
  code: string;
  name: string;
  category: string;
  weight: number;
  description: string;
  why_important: string;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "/api";

export async function analyzeText(text: string): Promise<AnalysisResult> {
  const res = await fetch(`${API_BASE}/analyze/text`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || "Terjadi kendala saat menganalisis teks lowongan.");
  }

  return res.json();
}

export async function analyzeUrl(url: string): Promise<AnalysisResult> {
  const res = await fetch(`${API_BASE}/analyze/url`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || "Kami belum dapat mengakses tautan lowongan ini. Silakan tempel teks secara manual.");
  }

  return res.json();
}

export async function analyzePhoto(file: File, fallbackText?: string): Promise<AnalysisResult> {
  if (file.size > 10 * 1024 * 1024) {
    throw new Error("Ukuran foto melebihi 10 MB. Kompres gambar atau pilih screenshot yang lebih kecil.");
  }

  const extractedText = fallbackText?.trim() || await extractTextFromImage(file);
  if (extractedText.length < 15) {
    throw new Error("Teks dari foto belum terbaca dengan jelas. Coba foto yang lebih tajam, lurus, dan memiliki kontras yang baik.");
  }

  const res = await fetch(`${API_BASE}/analyze/photo`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: extractedText, file_name: file.name }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || "Gagal menganalisis teks yang dibaca dari foto.");
  }

  return res.json();
}

function normalizeOcrText(text: string) {
  return text
    .replace(/\r/g, "")
    .replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/g, " ")
    .replace(/[ \t]+/g, " ")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
}

async function createOcrVariants(file: File): Promise<string[]> {
  const bitmap = await createImageBitmap(file);
  try {
    // Small screenshots are enlarged for legibility while large phone photos stay bounded in memory.
    const scale = Math.min(2, Math.max(1, 1600 / bitmap.width), 3600 / Math.max(bitmap.width, bitmap.height));
    const width = Math.max(1, Math.round(bitmap.width * scale));
    const height = Math.max(1, Math.round(bitmap.height * scale));
    const canvas = document.createElement("canvas");
    canvas.width = width;
    canvas.height = height;
    const context = canvas.getContext("2d", { willReadFrequently: true });
    if (!context) throw new Error("Browser tidak dapat menyiapkan gambar untuk OCR.");
    context.fillStyle = "#fff";
    context.fillRect(0, 0, width, height);
    context.drawImage(bitmap, 0, 0, width, height);

    const original = await canvasToDataUrl(canvas);
    const pixels = context.getImageData(0, 0, width, height);
    const data = pixels.data;
    for (let i = 0; i < data.length; i += 4) {
      const gray = 0.299 * data[i] + 0.587 * data[i + 1] + 0.114 * data[i + 2];
      // Stretch contrast to clarify text on pale or uneven screenshot backgrounds.
      const enhanced = Math.max(0, Math.min(255, (gray - 128) * 1.45 + 138));
      data[i] = enhanced;
      data[i + 1] = enhanced;
      data[i + 2] = enhanced;
    }
    context.putImageData(pixels, 0, 0);
    return [original, await canvasToDataUrl(canvas)];
  } finally {
    bitmap.close();
  }
}

function canvasToDataUrl(canvas: HTMLCanvasElement): Promise<string> {
  return new Promise((resolve, reject) => {
    canvas.toBlob((blob) => {
      if (!blob) {
        reject(new Error("Gambar tidak dapat dikonversi untuk OCR."));
        return;
      }
      const reader = new FileReader();
      reader.onload = () => typeof reader.result === "string"
        ? resolve(reader.result)
        : reject(new Error("Gambar tidak dapat dibaca oleh OCR."));
      reader.onerror = () => reject(new Error("Gambar tidak dapat dibaca oleh OCR."));
      reader.readAsDataURL(blob);
    }, "image/png");
  });
}

async function extractTextFromImage(file: File): Promise<string> {
  if (!file.type.startsWith("image/")) {
    throw new Error("Berkas harus berupa gambar PNG, JPG, atau JPEG.");
  }

  const [{ createWorker }, variants] = await Promise.all([
    import("tesseract.js"),
    createOcrVariants(file),
  ]);
  let worker: Awaited<ReturnType<typeof createWorker>>;
  try {
    worker = await createWorker("ind+eng", undefined, { logger: () => undefined });
  } catch (error) {
    console.error("Could not initialize browser OCR:", error);
    throw new Error("Mesin OCR tidak dapat dimuat. Pastikan koneksi internet aktif lalu coba kembali.");
  }

  try {
    await worker.setParameters({
      tessedit_pageseg_mode: "6" as import("tesseract.js").PSM,
      preserve_interword_spaces: "1",
    });
    let bestText = "";
    let bestScore = -1;

    // OCR both the original and contrast-enhanced image; screenshots often benefit from either treatment.
    for (const image of variants) {
      const { data } = await worker.recognize(image, { rotateAuto: true }, { text: true });
      const text = normalizeOcrText(data.text || "");
      const score = data.confidence + Math.min(text.length, 1500) / 100;
      if (score > bestScore) {
        bestText = text;
        bestScore = score;
      }
    }

    return bestText;
  } catch (error) {
    console.error("Browser OCR failed:", error);
    throw new Error("Mesin OCR gagal memproses gambar. Pastikan koneksi internet aktif lalu coba unggah kembali.");
  } finally {
    await worker.terminate();
  }
}

export async function getPublicIndicators(): Promise<PublicIndicator[]> {
  try {
    const res = await fetch(`${API_BASE}/public-indicators`);
    if (res.ok) return await res.json();
  } catch (err) {
    console.warn("Using fallback indicators list", err);
  }
  return [];
}

// Admin API
export async function adminLogin(email: string, password: string) {
  const res = await fetch(`${API_BASE}/admin/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Email atau kata sandi admin tidak sesuai.");
  }

  return res.json();
}

export async function getAdminDashboard(token: string): Promise<AdminDashboardStats> {
  const res = await fetch(`${API_BASE}/admin/dashboard`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error("Gagal memuat statistik dashboard.");
  return res.json();
}

export async function getAdminAnalyses(
  token: string,
  q?: string,
  level?: string
): Promise<{ items: AdminAnalysisRecord[]; count: number }> {
  const params = new URLSearchParams();
  if (q) params.set("q", q);
  if (level) params.set("level", level);

  const res = await fetch(`${API_BASE}/admin/analyses?${params.toString()}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error("Gagal memuat riwayat analisis.");
  return res.json();
}

export async function getAdminIndicators(token: string): Promise<{
  indicators: AdminIndicator[];
  total_weight: number;
  is_valid_total: boolean;
}> {
  const res = await fetch(`${API_BASE}/admin/indicators`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error("Gagal memuat daftar indikator.");
  return res.json();
}

export async function updateAdminIndicator(
  token: string,
  code: string,
  data: { weight: number; is_active: boolean; description: string }
) {
  const res = await fetch(`${API_BASE}/admin/indicators/${code}`, {
    method: "PUT",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Gagal memperbarui indikator.");
  return res.json();
}

export async function getAdminSettings(token: string): Promise<AdminSettings> {
  const res = await fetch(`${API_BASE}/admin/settings`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error("Gagal memuat pengaturan sistem.");
  return res.json();
}

export async function updateAdminSettings(token: string, data: Partial<AdminSettings>) {
  const res = await fetch(`${API_BASE}/admin/settings`, {
    method: "PUT",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Gagal menyimpan pengaturan.");
  return res.json();
}
