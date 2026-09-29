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
  const formData = new FormData();
  formData.append("file", file);
  if (fallbackText) {
    formData.append("fallback_text", fallbackText);
  }

  const res = await fetch(`${API_BASE}/analyze/photo`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || "Teks dalam foto belum dapat dibaca secara jelas. Silakan salin teks ke tab Teks.");
  }

  return res.json();
}

export async function getPublicIndicators(): Promise<any[]> {
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

export async function getAdminDashboard(token: string) {
  const res = await fetch(`${API_BASE}/admin/dashboard`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error("Gagal memuat statistik dashboard.");
  return res.json();
}

export async function getAdminAnalyses(token: string, q?: string, level?: string) {
  const params = new URLSearchParams();
  if (q) params.set("q", q);
  if (level) params.set("level", level);

  const res = await fetch(`${API_BASE}/admin/analyses?${params.toString()}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error("Gagal memuat riwayat analisis.");
  return res.json();
}

export async function getAdminIndicators(token: string) {
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

export async function getAdminSettings(token: string) {
  const res = await fetch(`${API_BASE}/admin/settings`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error("Gagal memuat pengaturan sistem.");
  return res.json();
}

export async function updateAdminSettings(token: string, data: any) {
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
